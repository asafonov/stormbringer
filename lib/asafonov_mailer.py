import lib.asafonov_pop3, lib.asafonov_imap, lib.asafonov_smtp, json, re

class mailer:

    def __init__(self, program_folder=''):
        self.program_folder = program_folder
        f = open(self.program_folder+'config/access')
        self.mailboxes = json.loads(f.read())
        f.close()
        self.connectMailbox(list(self.mailboxes.keys())[0])
        self.initFilters()

    def connectMailbox(self, mailbox):
        if mailbox in self.mailboxes:
            if self.mailboxes[mailbox]['protocol'] == 'IMAP':
                self.transport = lib.asafonov_imap.imapConnector(self.program_folder)
            else:
                self.transport = lib.asafonov_pop3.pop3Connector(self.program_folder)
            self.transport.host = self.mailboxes[mailbox]['in_host']
            self.transport.port = self.mailboxes[mailbox]['in_port']
            self.transport.login = self.mailboxes[mailbox]['login']
            self.transport.password = self.mailboxes[mailbox]['password']
            self.transport.is_ssl = int(self.mailboxes[mailbox]['in_is_ssl'])
            self.sender = lib.asafonov_smtp.smtpConnector(self.program_folder)
            self.sender.host = self.mailboxes[mailbox]['out_host']
            self.sender.port = self.mailboxes[mailbox]['out_port']
            self.sender.login = self.mailboxes[mailbox]['login']
            self.sender.password = self.mailboxes[mailbox]['password']
            self.sender.is_ssl = int(self.mailboxes[mailbox]['out_is_ssl'])
            self.sender.from_email=self.mailboxes[mailbox]['from']
            return True
        else:
            return False


    def initFilters(self):
        f = open(self.program_folder+'config/filters')
        self.filters = json.loads(f.read())
        f.close()

    def getMessageList(self):
        self.mail_list = self.transport.getMessageList()
        if len(self.filters)>0:
            self.applyFilters()
        return self.mail_list

    def applyFilters(self):
        spam = list(self.mail_list)
        for mail_item in spam:
            for i in range(len(self.filters)):
                applied = True
                for (f, filter_item) in self.filters[i].items():
                    if f!='Action':
                        if not re.match(filter_item, mail_item[f]):
                            applied = False
                if applied:
                    self.filterAction(mail_item, self.filters[i]['Action'])

    def filterAction(self, item, action):
        if (action=='hide'):
            self.mail_list.remove(item)
        if (action=='delete'):
            index = self.mail_list.index(item)
            self.mail_list.remove(item)
            self.deleteMessage(index+1)

    def getMessage(self, num):
        return self.transport.getMessage(num)
        
    def sendMessage(self, v_to, v_subject, v_msg, filenames, attach_dir, v_cc):
        self.sender.sendMessage(v_to, v_subject, v_msg, filenames, attach_dir, v_cc)

    def deleteMessage(self, num):
        self.transport.deleteMessage(num)
