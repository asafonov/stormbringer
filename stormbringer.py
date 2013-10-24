import sys
import lib.asafonov_mailer, lib.asafonov_folders

class stormbringer():

    commands = ['ls', 'cat']

    def __init__(self, program_folder=''):
        lib.asafonov_folders.initFolders(program_folder)
        lib.asafonov_folders.clearCache(program_folder)
        self.program_folder = program_folder
        self.mailer=lib.asafonov_mailer.mailer(program_folder)
        print('Welcome to Stormbringer, the world best email client!')
        cmd = ''
        while cmd!='exit':
            cmd = input('> ')
            self.processCommand(cmd)

    def processCommand(self, cmd):
        spam = cmd.split(' ')
        if spam[0]=='ls':
            if len(spam)==1:
                spam.append(0)
            if len(spam)==2:
                spam.append('inbox')
            self.printMessageList(spam[2], spam[1])

    def printMessageList(self, folder='inbox', limit=0):
        if folder=='inbox':
            self.printList(self.mailer.getMessageList(), limit)
        elif folder=='archive':
            self.printList(lib.asafonov_folders.getArchiveFolderItems(self.program_folder), limit)
        else:
            self.error('Unknown folder: '+folder)

    def printList(self, message_list, limit):
        cnt = len(self.message_list)
        print_limit = cnt
        if limit>0:
            print_limit = min(cnt, limit)
        for i in range(print_limit):
            print(str(i+1)+'. '+self.message_list[cnt-i-1]['Subject']+' '+self.message_list[cnt-i-1]['From']+' '+self.message_list[cnt-i-1]['Date'])


    def error(self, text):
        print('ERROR: '+text)


if len(sys.argv)>1:
    program_folder = sys.argv[1]
else:
    program_folder = ''
spam = stormbringer(program_folder = program_folder)