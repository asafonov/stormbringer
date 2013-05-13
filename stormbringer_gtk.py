from gi.repository import Gtk
import sys
import lib.asafonov_mailer, lib.asafonov_folders

class emailGui(Gtk.Window):
    def __init__(self, program_folder=''):
        Gtk.Window.__init__(self, title="Stormbringer")
        self.program_folder = program_folder
        self.createWidgets()
        self.mailer=lib.asafonov_mailer.mailer(program_folder)
        try:
            self.printMessageList()
        except Exception:
            self.printArchiveMessageList()

    def createToolbar(self):
        toolbar = Gtk.Toolbar()
        self.grid.attach(toolbar, 0, 0, 3, 1)

        compose_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_NEW)
        toolbar.insert(compose_button, 0)
        reply_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_UNDO)
        toolbar.insert(reply_button, 1)
        delete_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_REMOVE)
        toolbar.insert(delete_button, 2)
        #button_bold.connect("clicked", self.on_button_clicked, self.tag_bold)
        #button_italic.connect("clicked", self.on_button_clicked, self.tag_italic)
        #button_underline.connect("clicked", self.on_button_clicked, self.tag_underline)

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
        self.grid.attach(treeview,0,1,3,1)

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


if len(sys.argv)>1:
    program_folder = sys.argv[1]
else:
    program_folder = ''

win = emailGui(program_folder=program_folder)
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()