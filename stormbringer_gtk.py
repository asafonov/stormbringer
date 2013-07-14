from gi.repository import Gtk
import sys, re
import lib.asafonov_mailer, lib.asafonov_folders

class emailGui(Gtk.Window):

    message={}

    def __init__(self, program_folder=''):
        Gtk.Window.__init__(self, title="Stormbringer")
        self.program_folder = program_folder
        self.createWidgets()
        self.mailer=lib.asafonov_mailer.mailer(program_folder)
        try:
            self.printMessageList()
            self.folder='inbox'
        except Exception:
            self.printArchiveMessageList()
            self.folder='archive'

    def createToolbar(self):
        toolbar = Gtk.Toolbar()
        self.grid.attach(toolbar, 0, 0, 3, 1)

        compose_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_NEW)
        toolbar.insert(compose_button, 0)
        reply_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_UNDO)
        toolbar.insert(reply_button, 1)
        delete_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_REMOVE)
        toolbar.insert(delete_button, 2)
        compose_button.connect("clicked", self.compose)
        reply_button.connect("clicked", self.reply)
        #button_underline.connect("clicked", self.on_button_clicked, self.tag_underline)

    def compose(self, widget):
        win = composeForm(program_folder=self.program_folder)
        win.show_all()
        win.maximize()
        
    def reply(self, widget):
        if 'From' in self.message:
            if 'Cc' in self.message:
                cc=self.message['Cc']
            else:
                cc=''
            win = composeForm(program_folder=self.program_folder, v_to=self.message['From'], v_subject=self.message['Subject'], v_msg=self.message['plain'], v_cc=cc)
            win.show_all()
            win.maximize()
        else:
            self.compose(widget)

    def printMessageList(self):
        self.message_list = self.mailer.getMessageList()
        self.printList()

    def createList(self):
        self.liststore = Gtk.ListStore(str, str, str, str)
        treeview = Gtk.TreeView(model=self.liststore)
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Num", renderer_text, text=0)
        treeview.append_column(column_text)
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Subject", renderer_text, text=1)
        column_text.set_expand(True)
        treeview.append_column(column_text)
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("From", renderer_text, text=2)
        treeview.append_column(column_text)
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Date", renderer_text, text=3)
        treeview.append_column(column_text)
        treeview.connect("cursor-changed", self.onTreeviewChanged)
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        scrolledwindow.add(treeview)
        self.grid.attach(scrolledwindow,0,1,3,1)

    def onTreeviewChanged(self, widget):
        if widget.get_selection()!=None:
            selected_message = len(self.message_list)-int(widget.get_selection().get_selected()[0].get_value(widget.get_selection().get_selected()[1], 0))+1
            if (selected_message>0):
                self.selected_message = selected_message
                self.printMessage()


    def createText(self):
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        self.grid.attach(scrolledwindow,0,2,3,1)
        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.set_text("")
        scrolledwindow.add(self.textview)


    def createWidgets(self):
        self.grid = Gtk.Grid()
        self.add(self.grid)
        self.createToolbar()
        self.createList()
        self.createText()

    def printList(self):
        self.liststore.clear()
        cnt = len(self.message_list)
        for i in range(cnt):
            tmp = [str(i+1), self.message_list[cnt-i-1]['Subject'], self.message_list[cnt-i-1]['From'], self.message_list[cnt-i-1]['Date']]
            self.liststore.append(tmp)

    #
    # -- printArchiveMessageList
    # prints archive messages
    #
    def printArchiveMessageList(self):
        self.message_list = lib.asafonov_folders.getArchiveFolderItems(self.program_folder)
        self.printList()

    def printMessage(self):
        if (self.folder=='inbox'):
            self.message = self.mailer.getMessage(self.selected_message)
        elif(self.folder=='archive'):
            self.message = self.message_list[self.selected_message-1]
        self.printBody()

    def printBody(self):
        if 'plain' in self.message:
            body = self.message['plain']
        elif 'html' in self.message:
            body = re.sub('<[^>]*>', '', re.sub('<br[^>]*>', '\n', self.message['html']))
        else:
            body = ''
        self.textbuffer.set_text(body)

class composeForm(Gtk.Window):

    def __init__(self, v_to='', v_subject='', v_msg='', v_cc='', program_folder=''):
        Gtk.Window.__init__(self, title="Stormbringer. Compose message")
        self.program_folder = program_folder
        self.mailer=lib.asafonov_mailer.mailer(program_folder)
        self.createWidgets(v_to, v_subject, v_msg, v_cc)

    def createWidgets(self, v_to, v_subject, v_msg, v_cc):
        f = open(self.program_folder+'config/signature')
        if v_msg=='':
            v_msg = '\n\n'+f.read()
        else:
            v_msg = '\n\n'+f.read()+"\n\n"+v_msg
        f.close()
        self.grid = Gtk.Grid()
        self.add(self.grid)

        to_label = Gtk.Label('To');
        self.grid.attach(to_label, 0, 0, 1, 1)
        self.to_input = Gtk.Entry();
        self.to_input.set_text(v_to)
        self.grid.attach(self.to_input, 1, 0, 1, 1)

        subject_label = Gtk.Label('Subject');
        self.grid.attach(subject_label, 0, 1, 1, 1)
        self.subject_input = Gtk.Entry();
        self.subject_input.set_text(v_subject)
        self.grid.attach(self.subject_input, 1, 1, 1, 1)

        cc_label = Gtk.Label('Cc');
        self.grid.attach(cc_label, 0, 2, 1, 1)
        self.cc_input = Gtk.Entry();
        self.cc_input.set_text(v_cc)
        self.grid.attach(self.cc_input, 1, 2, 1, 1)

        body_label = Gtk.Label('Message');
        self.grid.attach(body_label, 0, 3, 1, 1)
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        self.grid.attach(scrolledwindow,1,3,1,1)
        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.set_text(v_msg)
        scrolledwindow.add(self.textview)

        button = Gtk.Button('Send')
        self.grid.attach(button, 1, 4, 1, 1)
        button.connect("clicked", self.sendMessage)

    def sendMessage(self, widget):
        filenames = []
        attach_dir = ''
        v_to = self.to_input.get_text()
        v_subject = self.subject_input.get_text()
        start, end = self.textbuffer.get_bounds()
        v_msg = self.textbuffer.get_text(start, end, True)
        v_cc = self.cc_input.get_text()
        self.mailer.sendMessage(v_to, v_subject, v_msg.replace('\n', '<br />'), filenames, attach_dir, v_cc)

if len(sys.argv)>1:
    program_folder = sys.argv[1]
else:
    program_folder = ''

win = emailGui(program_folder=program_folder)
win.connect("delete-event", Gtk.main_quit)
win.show_all()
win.maximize()
Gtk.main()
