# -*- coding: utf-8 -*-
import imaplib, os, sys
import lib.asafonov_email_parser

class imapConnector:
    host = ''
    port = ''
    login = ''
    password = ''
    is_ssl = 0
    is_cache = 1

    def __init__(self, program_folder=''):
        self.program_folder = program_folder

    def connect(self):
        if self.is_ssl>0:
            M = imaplib.IMAP4_SSL(self.host, self.port)
        else:
            M = imaplib.IMAP4(self.host, self.port)
        M.login(self.login, self.password)
        return M

    def getMessageList(self):
        M = self.connect()
        numMessages = int(M.select('INBOX')[1][0])
        nums = M.search(None, 'ALL')[1]
        message_list = []
        i=0
        if nums[0]!=None:
            for num in nums[0].split():
                data = M.fetch(num, '(BODY.PEEK[HEADER])')[1][0][1]
                spam = str(data).replace('\\n', '\n').replace('\\r', '')
                message_list.append(lib.asafonov_email_parser.parseEmailHeaders(spam))
                message_list[i]['num'] = i+1
                i=i+1
        M.close()
        M.logout()
        return message_list

    def getMessageNum(self):
        M = self.connect()
        numMessages = int(M.select('INBOX')[1][0])
        M.close()
        M.logout()
        return messageNum

    def getMessage(self, num):
        M = self.connect()
        numMessages = int(M.select('INBOX')[1][0])
        data = M.fetch(str(num), '(BODY.PEEK[HEADER])')[1][0][1]
        spam = str(data).replace('\\n', '\n').replace('\\r', '')
        headers = lib.asafonov_email_parser.parseEmailHeaders(spam)
        message={}
        message = lib.asafonov_email_parser.getMessageFromCache(headers['Message-Id'], None, self.program_folder)
        if not 'From' in message:
            data = M.fetch(str(num), '(RFC822)')[1][0][1]
            spam = str(data).replace('\\n', '\n').replace('\\r', '')
            enc = lib.asafonov_email_parser.getMessageEncoding(spam)
            spam = data.decode(enc, 'replace').replace('\r', '')
            message = lib.asafonov_email_parser.parseEmailBody(spam, self.program_folder)
            if self.is_cache>0:
                lib.asafonov_email_parser.saveMessageToCache(message, None, self.program_folder)
        M.close()
        M.logout()
        return message

    def deleteMessage(self, num):
        M = self.connect()
        numMessages = int(M.select('INBOX')[1][0])
        if self.host.lower()=='imap.gmail.com':
            import re
            resp, data = M.fetch(str(num), "(UID)")
            tmp = re.search('(?i)[0-9 ]\(UID ([0-9]+)\)', data[0].decode('utf-8'))
            if tmp!=None:
                uid = tmp.group(1)
                M.uid('COPY', uid, '[Gmail]/Trash')
        else:
            M.store(str(num), '+FLAGS', '(\Deleted)')
        M.expunge()
        M.close()
        M.logout()
