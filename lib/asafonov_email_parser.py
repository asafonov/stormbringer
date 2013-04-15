# -*- coding: utf-8 -*-
import re
import base64
import quopri
import os
import sys

def getMessageEncoding(msg):
    if re.match('(?s).*Content-Type: text/plain;.*?charset="{0,1}([A-Za-z0-9\-]*).*', msg):
        tmp = re.search('(?s)Content-Type: text/plain;.*?charset="{0,1}([A-Za-z0-9\-]*).*', msg)
        return tmp.group(1)
    if re.match('(?s).*Content-Type: text/html;.*?charset="{0,1}([A-Za-z0-9\-]*).*', msg):
        tmp = re.search('(?s)Content-Type: text/html;.*?charset="{0,1}([A-Za-z0-9\-]*).*', msg)
        return tmp.group(1)
    if re.match('(?s).*Subject:[ ]*=\?([A-Za-z0-9\-]+)\?.*', msg):
        tmp = re.search('(?s)Subject:[ ]*=\?([A-Za-z0-9\-]+)\?.*', msg)
        return tmp.group(1)
    return 'utf-8'

def encodeHeader(header):
    if sys.version_info[0] == 3:
        encoded = base64.b64encode(header.encode('utf-8'))
    else:
        encoded = base64.b64encode(header)
    if type(encoded)==bytes:
        out = '=?utf-8?B?'+encoded.decode('utf-8')+'?='
    else:
        out = '=?utf-8?B?'+encoded+'?='
    return out

def decodeHeaderItem(header):
    if re.match('=\?([A-Za-z0-9\-]+)\?([A-Z]+)\?(.*)\?=', header):
        out=''
        tmp = re.search('=\?([A-Za-z0-9\-]+)\?([A-Z]+)\?(.*)\?=', header)
        if tmp.group(2)=='B':
            out = base64.b64decode(tmp.group(3).encode('utf-8')).decode(tmp.group(1), 'replace')
        if tmp.group(2)=='Q':
            out = quopri.decodestring(tmp.group(3).encode('utf-8')).decode(tmp.group(1), 'replace')
    else:
        out = header
    return out

def decodeHeader(header):
    spam = re.findall('(?si)=\?[A-Za-z0-9\-]+\?[A-Z]+\?.*?\?=',header)
    if len(spam)>0:
        for i in range(len(spam)):
            header = header.replace(spam[i], decodeHeaderItem(spam[i]))
    return header.replace('\n ', '').replace('\n', '')

def decodeContentType(part):
    tmp = re.search('(?si)Content-Type: +(.*?)(?: |\n|;)', part)
    if tmp!=None:
        content_type = tmp.group(1)
    else:
        content_type = ''
    tmp = re.search('charset="{0,1}([A-Za-z0-9\-]+)', part)
    if tmp!=None:
        enc = tmp.group(1)
    else:
        enc = ''
    tmp = re.search('(?s).*?(?:\n\n|\r\n\r\n)(.*)', part)
    if tmp!=None:
        body = tmp.group(1)
    else:
        body = ''
    tmp = re.search('(?si)(content-disposition: *attachment)', part)
    if tmp == None:
        tmp = re.search('(?si)(content-disposition: *inline)', part)
    if tmp!=None:
        attachment = 1
        tmp = re.search('(?si)content-type:.*?(?:\n\n|\r\n\r\n)(.*)', body)
        if tmp!=None:
            body = tmp.group(1)
    else:
        attachment = 0
    tmp = re.search('Content-Transfer-Encoding: +([a-zA-Z0-9\-]*)', part)
    if tmp!=None:
        cte = tmp.group(1)
        if cte.lower() == 'base64' and (content_type=='text/plain' or content_type=='text/html') and attachment==0:
            if (enc==''):
                body = base64.b64decode(body.encode('utf-8')).decode('utf-8', 'replace')
            else:
                body = base64.b64decode(body.encode('utf-8')).decode(enc, 'replace')
        if cte.lower() == 'quoted-printable' and (content_type=='text/plain' or content_type=='text/html') and attachment==0:
            if enc=='':
                body = quopri.decodestring(body.encode('utf-8')).decode('utf-8')
            else:
                body = quopri.decodestring(body.encode('utf-8')).decode(enc)

    tmp = re.search('(?si)filename="{0,1}(.*?)(?:"|\n)', part)
    if tmp!=None:
        filename = decodeHeader(tmp.group(1))
    else:
        filename = ''
    tmp = re.search('(?si)Content-Id: *<([^>]*)>', part)
    if tmp!=None:
        content_id = tmp.group(1)
    else:
        content_id = ''
    return content_type, enc, body, attachment, filename, content_id

def parseEmailBody(email_body, program_folder=''):
    out = parseEmailHeaders(email_body)
    if (out['boundary']!=''):
        if 'additional_boundary' in out:
            email_body = email_body.replace(out['additional_boundary'], out['boundary'])
        parts = email_body.split(out['boundary'])
        out['attachments'] = []
        out['content_id'] = {}
        for i in range(2,len(parts)):
            type, enc, body, attachment, filename, content_id = decodeContentType(parts[i])
            if type=='text/html':
                body = re.sub('(?si)<head>.*?<\/head>', '', body)
                out['html'] = body
            if type=='text/plain':
                out['plain'] = body
            if attachment == 1:
                spam = {}
                spam['name'] = filename
                letter_dir = program_folder+'cache/'+out['Message-Id']
                if not os.path.exists(letter_dir):
                    os.makedirs(letter_dir)
                if re.search('[^A-Za-z0-9_\. \-]', filename):
                    filename = str(i)+re.sub('[^A-Za-z0-9_\. \-]', '', filename)
                #if there is no extention - adding default
                if not re.search('\.', filename):
                    filename += '.bin'
                spam['filename'] = '/cache/'+out['Message-Id']+'/'+filename
                f = open(letter_dir+'/'+filename, 'wb')
                f.write(base64.b64decode(body.encode('utf-8')))
                f.close()
                out['attachments'].append(spam)
                if content_id!='':
                    out['content_id'][content_id] = spam

        if 'html' in out:
            img = re.findall('<img[^>]*src="cid:([^"]*)"', out['html'])
            for i in range(len(img)):
                if img[i] in out['content_id']:
                    out['html'] = out['html'].replace('cid:'+img[i], out['content_id'][img[i]]['filename'])

    else:
        type, enc, body, attachment, filename, content_id = decodeContentType(email_body)
        if type=='text/html' or type=='':
            body = re.sub('(?si)<head>.*?<\/head>', '', body)
            out['html'] = body
            #out['html'] = re.sub('(?si)<img[^>]*>', '', body)
        if type=='text/plain':
            out['plain'] = body
    return out

def parseEmailHeaders(email_body):
    out = {}
    tmp = re.search('(?s)From: (.*?[A-Za-z0-9_\.\-]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,}.*?)\'*(?:\n[A-Za-z\-]+:|\n{1,})', email_body)
    out['From'] = decodeHeader(tmp.group(1))
    tmp = re.search('(?s)To: (.*?[A-Za-z0-9_\.\-]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,}.*?)\'*(?:\n[A-Za-z\-]+:|\n{1,})', email_body)
    if tmp!=None:
        out['To'] = decodeHeader(tmp.group(1))
    else:
        out['To'] = ''
    tmp = re.search('(?si)Cc: (.*?[A-Za-z0-9_\.\-]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,}.*?)\'*(?:\n[A-Za-z\-]+:|\n{1,})', email_body)
    if tmp!=None:
        out['Cc'] = decodeHeader(tmp.group(1))
    tmp = re.search('(?s)Subject: (.*?)\'*(?:\n[A-Za-z\-]+:|\n{2,})', email_body)
    if tmp!=None:
        out['Subject'] = decodeHeader(tmp.group(1))#.replace("'b'","")
    else:
        out['Subject'] = ''
    tmp = re.search('(?s)Date: (.*?)\'*\n', email_body)
    out['Date'] = decodeHeader(tmp.group(1))
    tmp = re.findall('(?s)boundary="{0,1}([A-Za-z0-9=_\.\-]*)', email_body)
    if len(tmp)>0:
        out['boundary'] = decodeHeader(tmp[len(tmp)-1])
    else:
        out['boundary'] = ''
    if len(tmp)>1:
        out['additional_boundary'] = decodeHeader(tmp[0])
    tmp = re.search('(?si)Message-Id: +([^\n]*)', email_body)
    if tmp!=None:
        out['Message-Id'] = re.sub('[^A-Za-z0-9_\.@\-]', '', tmp.group(1))
    else:
        out['Message-Id'] = ''
    return out

def getMessageFromCache(message_id, letter_file=None, program_folder=''):
    if letter_file==None:
        letter_file = program_folder+'cache/'+message_id+'.eml'
        attach_dir = program_folder+'cache/'+str(message_id)
        attach_prefix = '/cache/'+str(message_id)
    else:
        attach_dir = letter_file[0:len(letter_file)-4]
        attach_prefix = '/'+attach_dir.replace('../', '')

    out = {}
    if os.path.exists(letter_file):
        f = open(letter_file, 'rb')
        spam = f.read().decode('utf-8')
        f.close()
        tmp = re.search('(?s)<<From>>:(.*?)\n', spam)
        if tmp!=None:
            out['From'] = tmp.group(1)
        tmp = re.search('(?s)<<Subject>>:(.*?)\n', spam)
        if tmp!=None:
            out['Subject'] = tmp.group(1)
        tmp = re.search('(?s)<<To>>:(.*?)\n', spam)
        if tmp!=None:
            out['To'] = tmp.group(1)
        tmp = re.search('(?s)<<Message-Id>>:(.*?)\n', spam)
        if tmp!=None:
            out['Message-Id'] = tmp.group(1)
        tmp = re.search('(?s)<<Date>>:(.*?)\n', spam)
        if tmp!=None:
            out['Date'] = tmp.group(1)
        tmp = re.search('(?s)<<plain>>:(.*?)<<html>>', spam)
        if tmp!=None:
            out['plain'] = tmp.group(1)
        tmp = re.search('(?s)<<html>>:(.*?)<<taf>>', spam)
        if tmp!=None:
            out['html'] = tmp.group(1)
        tmp = re.search('(?s)<<Cc>>:(.*?)\n', spam)
        if tmp!=None:
            out['Cc'] = tmp.group(1)
        if os.path.exists(attach_dir):
            out['attachments'] = []
            spam = os.listdir(attach_dir)
            for i in range(len(spam)):
                tmp = {}
                tmp['filename'] = attach_prefix+'/'+spam[i]
                out['attachments'].append(tmp)
    return out

def saveMessageToCache(message, letter_file=None, program_folder=''):
    if letter_file==None:
        letter_file = program_folder+'cache/'+message['Message-Id']+'.eml'
    content = '<<From>>:'+message['From']+'\n'
    content += '<<Subject>>:'+message['Subject']+'\n'
    content += '<<To>>:'+message['To']+'\n'
    content += '<<Message-Id>>:'+message['Message-Id']+'\n'
    content += '<<Date>>:'+message['Date']+'\n'
    if 'Cc' in message:
        content += '<<Cc>>:'+message['Cc']+'\n'
    if 'plain' in message:
        content += '<<plain>>:'+message['plain']+'\n'
    else:
        content += '<<plain>>'
    if 'html' in message:
        content += '<<html>>:'+message['html']+'\n'
    else:
        content += '<<html>>'
    content += '<<taf>>'
    if sys.version_info[0] == 3:
        f = open(letter_file, 'wb')
        f.write(content.encode('utf-8'))
        f.close()
    else:
        f = open(letter_file, 'wb')
        f.write(content.encode('utf-8'))
        f.close()
