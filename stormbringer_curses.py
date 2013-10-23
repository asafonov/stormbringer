import curses, sys, json, re
import lib.asafonov_mailer, lib.asafonov_folders

class emailGui:

    message_list = []

    def __init__(self, program_folder):
        self.mailer=lib.asafonov_mailer.mailer(program_folder)
        try:
            self.folder='inbox'
        except Exception:
            self.folder='archive'
        self.program_folder = program_folder
        f = open(self.program_folder+'config/keyconfig')
        self.keyconfig = json.loads(f.read())
        f.close()

        x = 0

        while x!=self.keyconfig['quit']:
            if x==self.keyconfig['refresh']:
                self.printMessageList(True)
            elif x>=ord('1') and x<=ord('9'):
                self.printMessage(int(chr(x)))
            else:
                self.printMessageList()
                if x>0:
                    self.myscreen.addstr(self.myscreen.getmaxyx()[0]-1, 2, "No hotkey for "+str(x))

            self.myscreen.refresh()
            x = self.myscreen.getch()

        curses.endwin()

    def createScreen(self):
        self.myscreen = curses.initscr()
        self.myscreen.clear()
        self.myscreen.border(0)
        self.myscreen.addstr(0, 2, "Stormbringer")

    def printMessage(self, num):
        self.selected_message = len(self.message_list) - num + 1
        if (self.folder=='inbox'):
            self.message = self.mailer.getMessage(self.selected_message)
        elif(self.folder=='archive'):
            self.message = self.message_list[self.selected_message-1]
        self.printBody()

    def printBody(self):
        self.createScreen()
        if 'plain' in self.message:
            body = self.message['plain']
        elif 'html' in self.message:
            body = re.sub('<[^>]*>', '', re.sub('<br[^>]*>', '\n', self.message['html']))
        else:
            body = ''
        regexp = re.compile("(.{"+str(self.myscreen.getmaxyx()[1]-4)+"})")
        body = regexp.sub(r"\1\n", body)
        body = re.sub("\n[\n\s\t]*\n", "\n", body)
        body = re.sub("^\n", '', body)
        spam = body.split("\n")
        self.myscreen.addnstr(2, 2, "From: "+self.message['From'], self.myscreen.getmaxyx()[1]-4)
        self.myscreen.addnstr(3, 2, "Subject: "+self.message['Subject'], self.myscreen.getmaxyx()[1]-4)
        self.myscreen.addnstr(4, 2, "", self.myscreen.getmaxyx()[1]-4)

        for i in range(min(len(spam), self.myscreen.getmaxyx()[0]-7)):
            self.myscreen.addnstr(i+5, 2, spam[i], self.myscreen.getmaxyx()[1]-4)


    def printMessageList(self, refresh=False):
        self.createScreen()
        refresh = refresh or len(self.message_list)==0
        if not refresh:
            self.printList()
        elif (self.folder=='inbox'):
            self.printInboxMessageList()
        elif(self.folder=='archive'):
            self.printArchiveMessageList()

    def printInboxMessageList(self):
        self.message_list = self.mailer.getMessageList()
        self.printList()

    def printArchiveMessageList(self):
        self.message_list = lib.asafonov_folders.getArchiveFolderItems(self.program_folder)
        self.printList()

    def printList(self):
        cnt = len(self.message_list)
        for i in range(cnt):
            tmp = str(i+1)+' '+self.message_list[cnt-i-1]['Subject']+' '+self.message_list[cnt-i-1]['From']
            self.myscreen.addnstr(i+2, 2, tmp, self.myscreen.getmaxyx()[1]-4)


if len(sys.argv)>1:
    program_folder = sys.argv[1]
else:
    program_folder = ''

asd = emailGui(program_folder = program_folder)