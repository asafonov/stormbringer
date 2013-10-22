import lib.asafonov_pop3, lib.asafonov_imap, lib.asafonov_smtp, json, re

class mailer:

    def __init__(self, program_folder=''):
        self.program_folder = program_folder
        f = open(self.program_folder+'config/access')
        lines = f.read().split('\n')
        f.close()
        self.protocol = lines[9]
        if self.protocol == 'IMAP':
            self.transport = lib.asafonov_imap.imapConnector(self.program_folder)
        else:
            self.transport = lib.asafonov_pop3.pop3Connector(self.program_folder)
        self.transport.host = lines[0]
        self.transport.port = lines[1]
        self.transport.login = lines[2]
        self.transport.password = lines[3]
        self.transport.is_ssl = int(lines[4])
        self.sender = lib.asafonov_smtp.smtpConnector(self.program_folder)
        self.sender.host = lines[5]
        self.sender.port = lines[6]
        self.sender.login = lines[2]
        self.sender.password = lines[3]
        self.sender.is_ssl = int(lines[7])
        self.sender.from_email=lines[8]
        self.initFilters()

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
