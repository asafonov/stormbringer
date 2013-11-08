# -*- coding: utf-8 -*-
import poplib, os, sys
import lib.asafonov_email_parser

class pop3Connector:
    host=''
    port=''
    login=''
    password=''
    is_ssl=0
    is_cache=1

    def __init__(self, program_folder=''):
        self.program_folder = program_folder


    def connect(self):
        if self.is_ssl>0:
            M=poplib.POP3_SSL(self.host, self.port)
        else:
            M=poplib.POP3(self.host, self.port)
        M.user(self.login)
        M.pass_(self.password)
        return M

    def getMessage(self, num):
        M = self.connect()
        j = M.top(num, 0)
        spam = ''
        for k in range(len(j[1])):
            spam += str(j[1][k])[2:-1]+'\n'
        headers = lib.asafonov_email_parser.parseEmailHeaders(spam)
        message={}
        message = lib.asafonov_email_parser.getMessageFromCache(headers['Message-Id'], None, self.program_folder)
        if not 'From' in message:
            lines = M.retr(num)[1]
            spam = str(b"\n".join(lines))
            enc = lib.asafonov_email_parser.getMessageEncoding(spam)
            spam = ''
            for i in range(len(lines)):
                spam += lines[i].decode(enc, 'replace')+'\n'
            message = lib.asafonov_email_parser.parseEmailBody(spam, self.program_folder)
            if self.is_cache>0:
                lib.asafonov_email_parser.saveMessageToCache(message, None, self.program_folder)
        M.quit()
        return message

    def getMessageNum(self):
        M = self.connect()
        numMessages = len(M.list()[1])
        M.quit()
        return numMessages

    def getMessageList(self):
        M = self.connect()
        numMessages = len(M.list()[1])
        message_list = []
        for i in range(numMessages):
            j = M.top(i+1,0)
            spam = ''
            for k in range(len(j[1])):
                if (sys.version_info[0]==3):
                    spam += str(j[1][k])[2:-1]+'\n'
                else:
                    spam += str(j[1][k])+'\n'
            message_list.append(lib.asafonov_email_parser.parseEmailHeaders(spam))
            message_list[i]['num'] = i+1
        M.quit()
        return message_list

    def deleteMessage(self, num):
        M = self.connect()
        M.dele(num)
        M.quit()
