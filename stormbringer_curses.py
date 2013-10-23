import curses, sys
import lib.asafonov_mailer, lib.asafonov_folders

class emailGui:

    message_list = []

    def __init__(self, program_folder):
        self.mailer=lib.asafonov_mailer.mailer(program_folder)
        try:
            self.folder='inbox'
        except Exception:
            self.folder='archive'

        x = 0

        while x!=ord('q'):
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
            self.myscreen.addstr(i+2, 2, tmp)


if len(sys.argv)>1:
    program_folder = sys.argv[1]
else:
    program_folder = ''

asd = emailGui(program_folder = program_folder)