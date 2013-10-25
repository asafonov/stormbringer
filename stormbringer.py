import sys,  json, re, os, shutil
import lib.asafonov_mailer, lib.asafonov_folders

class stormbringer():

    selected_message = 0

    def __init__(self, program_folder=''):
        lib.asafonov_folders.initFolders(program_folder)
        lib.asafonov_folders.clearCache(program_folder)
        self.program_folder = program_folder
        self.mailer=lib.asafonov_mailer.mailer(program_folder)
        print('Welcome to Stormbringer, the true hacker\'s email client')
        cmd = ''
        f = open(self.program_folder+'config/commands')
        self.commands = json.loads(f.read())
        f.close()
        listen = True
        while listen:
            cmd = input('> ')
            listen = self.processCommand(cmd)

    def processCommand(self, cmd):
        spam = cmd.split(' ')
        if spam[0] in self.commands.keys():
            cmd_name = self.commands[spam[0]]
        else:
            cmd_name = spam[0]
        if cmd_name=='ls':
            if len(spam)==1:
                spam.append(0)
            if len(spam)==2:
                spam.append('inbox')
            self.printMessageList(spam[2], int(spam[1]))
        elif cmd_name=='cat':
            if len(spam)==1:
                spam.append(1)
            self.printMessage(int(spam[1]))
        elif cmd_name=='new':
            self.createMessage()
        elif cmd_name=='rp':
            if len(spam)==1:
                spam.append(self.message_list_count - self.selected_message + 1)
            self.replyMessage(int(spam[1]))
        elif cmd_name=='rm':
            if len(spam)==1:
                spam.append(self.message_list_count - self.selected_message + 1)
            self.deleteMessage(int(spam[1]))
        elif cmd_name=='exit':
            return False
        else:
            self.error("Unknown command: "+spam[0])
        return True

    def replyMessage(self, num):
        selected_message = self.message_list_count - num + 1
        if selected_message!=self.selected_message:
            self.selected_message = selected_message
            self.getMessage()
        filenames = []
        attach_dir = ''
        v_to = input("To: "+self.message['From'])
        if (v_to==''):
            v_to = self.message['From']
        v_subject = input("Subject: Re: "+self.message['Subject'])
        if (v_subject==''):
            v_subject = self.message['Subject']
        if 'Cc' in self.message:
            v_cc = input("Cc: "+self.message['Cc'])
            if (v_cc==''):
                v_cc = self.message['Cc']
        else:
            v_cc = input("Cc: ")           
        v_msg = input('Body (Type "END" to commit): ')
        if v_msg=='END':
            v_msg = ''
        else:
            line = ''
            while line!='END':
                v_msg = v_msg + "\n"+ line
                line = input()
        f = open(self.program_folder+'config/signature')
        v_msg+="\n\n"+f.read()
        f.close()
        v_msg = v_msg+"\n\n"+"On "+self.message['Date']+' '+self.message['From']+' wrote: \n'+self.message['Body'].replace("\n", "\n> ")
        v_attach = input('Attachments (Filenames, divided with ";"): ')
        if len(v_attach)>0:
            attach_dir = self.program_folder+'tmp/attach'
            os.makedirs(attach_dir)
            attachments = v_attach.split(";")
            for i in range(len(attachments)):
                shutil.copy(attachments[i], attach_dir)
            filenames = os.listdir(attach_dir)
        self.mailer.sendMessage(v_to, v_subject, v_msg.replace('\n', '<br />'), filenames, attach_dir, v_cc)
        print("OK")

    def createMessage(self):
        filenames = []
        attach_dir = ''
        v_to = input("To: ")
        v_subject = input("Subject: ")
        v_cc = input("Cc: ")
        v_msg = input('Body (Type "END" to commit): ')
        if v_msg=='END':
            v_msg = ''
        else:
            line = ''
            while line!='END':
                v_msg = v_msg + "\n" + line
                line = input()
        f = open(self.program_folder+'config/signature')
        v_msg+="\n\n"+f.read()
        f.close()
        v_attach = input('Attachments (Filenames, divided with ";"): ')
        if len(v_attach)>0:
            attach_dir = self.program_folder+'tmp/attach'
            os.makedirs(attach_dir)
            attachments = v_attach.split(";")
            for i in range(len(attachments)):
                shutil.copy(attachments[i], attach_dir)
            filenames = os.listdir(attach_dir)
        self.mailer.sendMessage(v_to, v_subject, v_msg.replace('\n', '<br />'), filenames, attach_dir, v_cc)
        print("OK")

    def deleteMessage(self, num):
        self.mailer.deleteMessage(self.message_list_count - num + 1)
        print("OK")

    def printMessage(self, num):
        self.selected_message = self.message_list_count - num + 1
        self.getMessage()
        self.printBody()

    def getMessage(self):
        if (self.folder=='inbox'):
            self.message = self.mailer.getMessage(self.selected_message)
        elif(self.folder=='archive'):
            self.message = self.message_list[self.selected_message-1]
        if 'plain' in self.message:
            body = self.message['plain']
        elif 'html' in self.message:
            body = re.sub('<[^>]*>', '', re.sub('<br[^>]*>', '\n', self.message['html']))
        else:
            body = ''
        self.message['Body'] = body


    def printBody(self):
        body = self.message['Body']
        body = re.sub("\n[\n\s\t]*\n", "\n", body)
        body = re.sub("^\n", '', body)
        print("From: "+self.message['From'])
        print("Subject: "+self.message['Subject'])
        print("Date: "+self.message['Date'])
        print('')
        print(body)

    def printMessageList(self, folder='inbox', limit=0):
        if folder=='inbox':
            self.folder = folder
            self.printList(self.mailer.getMessageList(), limit)
        elif folder=='archive':
            self.folder = folder
            self.printList(lib.asafonov_folders.getArchiveFolderItems(self.program_folder), limit)
        else:
            self.error('Unknown folder: '+folder)

    def printList(self, message_list, limit):
        self.message_list_count = len(message_list)
        print_limit = self.message_list_count
        if int(limit)>0:
            print_limit = min(self.message_list_count, int(limit))
        if print_limit>0:
            for i in range(print_limit):
                print(str(i+1)+'. '+message_list[self.message_list_count-i-1]['Subject']+' '+message_list[self.message_list_count-i-1]['From']+' '+message_list[self.message_list_count-i-1]['Date'])
        else:
            print('No messages to display')

    def error(self, text):
        print('ERROR: '+text)


if len(sys.argv)>1:
    program_folder = sys.argv[1]
else:
    program_folder = ''
spam = stormbringer(program_folder = program_folder)