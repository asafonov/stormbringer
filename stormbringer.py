import sys,  json
import lib.asafonov_mailer, lib.asafonov_folders

class stormbringer():

    def __init__(self, program_folder=''):
        lib.asafonov_folders.initFolders(program_folder)
        lib.asafonov_folders.clearCache(program_folder)
        self.program_folder = program_folder
        self.mailer=lib.asafonov_mailer.mailer(program_folder)
        print('Welcome to Stormbringer, the world best email client!')
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
            self.printMessageList(spam[2], spam[1])
        elif cmd_name=='cat':
            if len(spam)==1:
                spam.append(1)
            self.printMessage(spam[1])
        elif cmd_name=='exit':
            return False
        else:
            self.error("Unknown command: "+spam[0])
        return True

    def printMessage(self, num):
        self.selected_message = self.message_list_count - num + 1
        if (self.folder=='inbox'):
            self.message = self.mailer.getMessage(self.selected_message)
        elif(self.folder=='archive'):
            self.message = self.message_list[self.selected_message-1]
        self.printBody()

    def printBody():
        if 'plain' in self.message:
            body = self.message['plain']
        elif 'html' in self.message:
            body = re.sub('<[^>]*>', '', re.sub('<br[^>]*>', '\n', self.message['html']))
        else:
            body = ''
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