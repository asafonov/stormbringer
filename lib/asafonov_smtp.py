# -*- coding: utf-8 -*-
import smtplib, re, os, base64, sys
import lib.asafonov_email_parser

class smtpConnector:
    host=''
    port=''
    login=''
    password=''
    is_ssl=0
    from_email = ''

    def __init__(self, program_folder=''):
        self.program_folder = program_folder

    def connect(self):
        pass

    def prepareMessage(self, v_to, v_subject, msg, filenames, attach_dir, v_cc=''):
        headers = 'MIME-Version: 1.0\n'
        headers += 'From: '+self.from_email+'\n'
        tmp = re.findall('[A-Za-z0-9_\.\-]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,}', v_to)
        v_to = ', '.join(tmp)
        headers+= 'To: '+v_to+'\n'
        if v_cc!='':
            tmp = re.findall('[A-Za-z0-9_\.\-]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,}', v_cc)
            v_cc = ', '.join(tmp)
            headers+= 'Cc: '+v_cc+'\n'
        v_subject = lib.asafonov_email_parser.encodeHeader(v_subject)
        headers+= 'Subject: '+v_subject+'\n'
        if len(filenames)>0:
            import uuid
            boundary = '----------'+str(uuid.uuid1())
            headers+='Mime-Version: 1.0\n'
            headers+='Content-Type:multipart/mixed;'
            headers+='boundary="'+boundary+'"\n\n'
            headers+='--'+boundary+'\n'
        headers+= 'Content-Type: text/html; charset=utf-8\n'
        headers+= 'Content-Transfer-Encoding: base64\n\n'
        if sys.version_info[0]==3:
            encoded_msg = base64.b64encode(msg.encode('utf-8'))
        else:
            encoded_msg = base64.b64encode(msg)
        if type(encoded_msg)==bytes:
            headers += encoded_msg.decode('utf-8')
        else:
            headers += encoded_msg
        for i in range(len(filenames)):
            headers+='\n\n--'+boundary+'\n'
            headers+='Content-Type: application/octet-stream;'
            headers+='name="'+filenames[i]+'"\n'
            headers+='Content-Transfer-Encoding:base64\n'
            headers+='Content-Disposition:attachment;'
            headers+='filename="'+filenames[i]+'"\n\n'
            f = open(attach_dir+'/'+filenames[i], 'rb')
            encoded_attach = base64.b64encode(f.read())
            if type(encoded_attach)==bytes:
                headers+=encoded_attach.decode('utf-8')
            else:
                headers+=encoded_attach
            f.close()
            os.remove(attach_dir+'/'+filenames[i])
        headers+='\n'
        if len(filenames)>0:
            os.rmdir(attach_dir)
        return headers

    def saveSentMessage(self, v_to, v_subject, msg):
        letter_file = self.program_folder+'sent/'+self.from_email
        if not os.path.exists(letter_file):
            os.makedirs(letter_file)
        tmp = re.search('(?si)[a-z0-9_\.\-]+@[a-z0-9\.\-]+\.[a-z]{2,6}', v_to)
        letter_file += '/'+tmp.group(0)
        if not os.path.exists(letter_file):
            os.makedirs(letter_file)
        from datetime import datetime
        sent_time = datetime.now().strftime('%Y%m%d%H%M%S')
        letter_file += '/'+sent_time
        message = {}
        message['From'] = self.from_email
        message['To'] = v_to
        message['Subject'] = v_subject
        message['Message-Id'] = sent_time
        message['Date'] = sent_time
        message['html'] = msg
        lib.asafonov_email_parser.saveMessageToCache(message, letter_file)

    def sendMessage(self, v_to, v_subject, msg, filenames, attach_dir, v_cc=''):
        self.connect()
        if self.is_ssl==1:
            M = smtplib.SMTP_SSL(self.host, self.port)
        else:
            M = smtplib.SMTP(self.host, self.port)
        v_msg = self.prepareMessage(v_to, v_subject, msg, filenames, attach_dir, v_cc)
        if self.port==587:
            M.starttls()
        M.login(self.login, self.password)
        tmp = re.findall('[A-Za-z0-9_\.\-]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,}', v_to)
        if v_cc!='':
            tmp += re.findall('[A-Za-z0-9_\.\-]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,}', v_cc)
        M.sendmail(self.from_email, tmp, v_msg)
        M.quit()
        self.saveSentMessage(v_to, v_subject, msg)

    def sendMessageSendmail(self, v_to, v_subject, msg, filenames, attach_dir, v_cc=''):
        self.connect()
        sendmail_location = '/usr/sbin/sendmail'
        p = os.popen("%s -t" % sendmail_location, "w")
        v_msg = self.prepareMessage(v_to, v_subject, msg, filenames, attach_dir)
        p.write(v_msg)
        status = p.close() 
        self.saveSentMessage(v_to, v_subject, msg)
        if status != 0: 
            print("Sendmail exit status: "+str(status))
