import lib.asafonov_pop3, lib.asafonov_imap, lib.asafonov_smtp

class mailer:

    def __init__(self, program_folder=''):
        self.program_folder = program_folder
        f = open(self.program_folder+'config/access')
        lines = f.read().split('\n')
        f.close()
        self.protocol = lines[8]
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
        self.sender.is_ssl = int(lines[4])
        self.sender.from_email=lines[7]

    def getMessageList(self):
        return self.transport.getMessageList()

    def getMessage(self, num):
        return self.transport.getMessage(num)
        
    def sendMessage(self, v_to, v_subject, v_msg, filenames, attach_dir, v_cc):
        self.sender.sendMessage(v_to, v_subject, v_msg, filenames, attach_dir, v_cc)
