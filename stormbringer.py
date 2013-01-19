#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, re, threading, shutil
if sys.version_info[0]>=3:
    from tkinter import *
    from tkinter import ttk
else:
    from Tkinter import *
    import ttk

import lib.asafonov_pop3, lib.asafonov_imap, lib.asafonov_smtp, lib.asafonov_folders

class emailGui(Frame):

    #
    # -- createMenu
    # creates main menu of the application
    #

    def createMenu(self):
        if self.colors['menu']=='0':
            return False
        else:
            self.menuBar = Menu(self)
            self.fileMenu = Menu(self.menuBar)
            self.menuBar.add_cascade(label="File", menu=self.fileMenu)
            self.fileMenu.add_command(label="Exit", command=self.quit)
            self.messagesMenu = Menu(self.menuBar)
            self.menuBar.add_cascade(label='Messages', menu=self.messagesMenu)
            self.messagesMenu.add_command(label='Check for new', command=self.checkEmails)
            self.messagesMenu.add_command(label='Archive current', command=self.archiveCurrent)
            self.viewMenu = Menu(self.menuBar)
            self.menuBar.add_cascade(label="View", menu=self.viewMenu)
            self.viewMenu.add_command(label='Inbox', command=self.checkEmails)
            self.viewMenu.add_command(label='Archive', command=self.checkArchive)
            return self.menuBar

    #
    # -- onMessageSelected
    # event for the selecting message by mouse click on the list
    # prints the selected message
    #

    def onMessageSelected(self, *event):
        cur_selection = self.emailList.index(self.emailList.focus())
        if self.selected_message!=self.total_messages - int(cur_selection):
            self.printMessageByNum(int(cur_selection+1))

    #
    # -- archiveCurrent
    # archives current message. To archive the message, Message-Id is required
    # which is taken from self.v_message_id
    #

    def archiveCurrent(self):
        if self.v_message_id!='':
            lib.asafonov_folders.saveArchiveMessage(self.v_message_id, self.program_folder)
            print('Message '+self.v_message_id+' saved')
    
    def createWidgets(self, master):
        self.selected_message=0
        self.v_to = ''
        self.v_cc = ''
        self.v_subject = ''
        self.v_msg = ''

        if self.colors['toolbar']=='1':
            self.buttonFrame = ttk.Frame(master)
            self.buttonFrame.pack(fill=X)
            self.composeImg = PhotoImage(file=self.program_folder+"images/compose.gif")
            self.composeButton = ttk.Button(self.buttonFrame, text='Compose', command=self.onComposeButton, image=self.composeImg)
            self.composeButton.grid(row=0, column=0)
            self.replyImg = PhotoImage(file=self.program_folder+"images/reply.gif")
            self.replyButton = ttk.Button(self.buttonFrame, text='Reply', command=self.onReplyButton, image=self.replyImg)
            self.replyButton.grid(row=0, column=1)
            self.replyButton['state'] = DISABLED
            self.deleteImg = PhotoImage(file=self.program_folder+"images/delete.gif")
            self.deleteButton = ttk.Button(self.buttonFrame, text='Delete', command=self.onDeleteButton, image=self.deleteImg)
            self.deleteButton.grid(row=0, column=2)
            self.deleteButton['state'] = DISABLED

        self.listFrame = ttk.Frame(master)
        self.listFrame.pack(fill=BOTH, expand=YES)
        self.emailListScroll = ttk.Scrollbar(self.listFrame)
        self.emailList = ttk.Treeview(self.listFrame, columns=('#', 'Subject', 'From', 'Date'), show='headings')
        self.emailList.pack(fill=BOTH, expand=YES, side=LEFT)
        self.emailList.heading('#', text='#')
        self.emailList.heading('Subject', text='Subject')
        self.emailList.heading('From', text='From')
        self.emailList.heading('Date', text='Date')
        self.emailList.column('Subject', width=600)
        self.emailList.column('#', width=1)
        self.emailList.config(yscrollcommand=self.emailListScroll.set)
        self.emailListScroll.config(command = self.emailList.yview)
        self.emailListScroll.pack(side=RIGHT, fill=Y)
        self.emailList.bind('<<TreeviewSelect>>', self.onMessageSelected)

        self.bodyFrame = ttk.Frame(master)
        self.bodyFrame.pack(fill=BOTH, expand=YES)
        self.emailBodyScroll = ttk.Scrollbar(self.bodyFrame)
        self.emailBody = Text(self.bodyFrame, width=136, height=20)
        self.emailBody['background'] = self.colors['background']
        self.emailBody['foreground'] = self.colors['text_foreground']
        self.emailBody.pack(expand=YES, fill=BOTH, side=LEFT)
        self.emailBody.config(yscrollcommand=self.emailBodyScroll.set)
        self.emailBodyScroll.config(command = self.emailBody.yview)
        self.emailBodyScroll.pack(side=RIGHT, fill=Y)

        ttk.Style().configure('Treeview', fieldbackground=self.colors['background'], background=self.colors['background'], foreground=self.colors['list_foreground'])

        self.statusLabel=ttk.Label(master)
        self.statusLabel.pack(fill=X)
        self.total_messages = 0
        self.getKeyConfig()
        self.bind('<Key>', self.onKeyPressed)
        self.getCredentials()
        self.checkEmails()

    def getKeyConfig(self):
        self.keyconfig = {}
        f = open(self.program_folder+'config/keyconfig')
        lines = f.read().split('\n')
        f.close()
        for i in range(len(lines)):
            tmp = lines[i].split(':')
            if len(tmp)>1:
                self.keyconfig[tmp[0]] = tmp[1]

    def onKeyPressed(self, event):
        req_action = None
        if event.keysym in self.keyconfig:
            req_action = self.keyconfig[event.keysym]
        if ('Ctrl+'+event.keysym in self.keyconfig) and (self.ctrl==1):
            req_action = self.keyconfig['Ctrl+'+event.keysym]
        if ('Alt+'+event.keysym in self.keyconfig) and (self.alt==1):
            req_action = self.keyconfig['Alt+'+event.keysym]
        if req_action != None:
            if req_action == 'printMessageByNum':
                self.printMessageByNum(int(event.keysym))
            if req_action == 'deleteMessageByNum':
                self.deleteMessageByNum(int(event.keysym))
            if req_action == 'checkEmails':
                self.checkEmails()
            if req_action == 'checkArchive':
                self.checkArchive()
            if req_action == 'reply':
                self.onReplyButton()
            if req_action == 'compose':
                self.onComposeButton()
            if req_action == 'quit':
                self.quit()
            if req_action == 'archiveCurrent':
                self.archiveCurrent()
        if (event.keysym=='Control_L') or (event.keysym=='Control_R'):
            self.ctrl = 1
        else:
            self.ctrl = 0
        if (event.keysym=='Alt_L') or (event.keysym=='Alt_R'):
            self.alt = 1
        else:
            self.alt = 0

    #
    # -- printMessageByNum
    # prints message by given number from the list of messages
    #

    def printMessageByNum(self,num):
        if self.folder == 'inbox':
            selected_message = self.total_messages + 1 - num
            if selected_message>0:
                self.selected_message = selected_message
                if self.colors['threading'] == '1':
                    threading.Thread(target=self.printInboxMessage).start()
                else:
                    self.printInboxMessage()
        if self.folder == 'archive':
            self.printMessage(self.message_list[self.total_messages - num])

    def deleteMessageByNum(self, num):
        selected_message = self.total_messages + 1 - num
        if selected_message>0:
            self.selected_message = selected_message
            if self.colors['threading'] == '1':
                threading.Thread(target=self.deleteMessage).start()
            else:
                self.deleteMessage()

    #
    # -- checkEmails
    # just a thread for displaying inbox messages
    # calls printMessageList
    # 

    def checkEmails(self):
        self.folder = 'inbox'
        self.message_list = []
        if self.colors['threading'] == '1':
            threading.Thread(target=self.printMessageList).start()
        else:
            self.printMessageList()

    #
    # -- checkArchive
    # just a thread for displaying archive messages
    # calls printArchiveMessageList
    #

    def checkArchive(self):
        self.folder = 'archive'
        if self.colors['threading'] == '1':
            threading.Thread(target=self.printArchiveMessageList).start()
        else:
            self.printArchiveMessageList()

    def getCredentials(self):
        f = open(self.program_folder+'config/access')
        lines = f.read().split('\n')
        f.close()
        self.pop3host = lines[0]
        self.pop3port = lines[1]
        self.login = lines[2]
        self.password = lines[3]
        self.is_ssl = lines[4]
        self.protocol = lines[8]

    #
    # -- printArchiveMessageList
    # prints archive messages
    #

    def printArchiveMessageList(self):
        self.message_list = lib.asafonov_folders.getArchiveFolderItems(self.program_folder)
        self.printList(self.message_list)
        
    #
    # -- printMessageList
    # prints inbox messages
    #

    def printMessageList(self):
        self.statusLabel['text']='checking for new emails...'
        if self.protocol == 'IMAP':
            mailer = lib.asafonov_imap.imapConnector(self.program_folder)
        else:
            mailer = lib.asafonov_pop3.pop3Connector(self.program_folder)
        mailer.host = self.pop3host
        mailer.port = self.pop3port
        mailer.login = self.login
        mailer.password = self.password
        mailer.is_ssl = int(self.is_ssl)
        message_list = mailer.getMessageList()
        self.printList(message_list)
        self.statusLabel['text']=''

    #
    # -- printList
    # prints the list of messages given as a parameter
    #

    def printList(self, message_list):
        items = self.emailList.get_children()
        for i in range(len(items)):
            self.emailList.delete(items[i])
        cnt = len(message_list)
        self.total_messages = cnt
        for i in range(cnt):
            self.emailList.insert('',0, values=(cnt-i,message_list[i]['Subject'], message_list[i]['From'], message_list[i]['Date']))

    #
    # -- printMessage
    # prints the given message
    #
            
    def printMessage(self, message):
        if 'plain' in message:
            body = message['plain']
        elif 'html' in message:
            body = re.sub('<[^>]*>', '', re.sub('<br[^>]*>', '\n', message['html']))
        else:
            body = ''
        self.emailBody.delete(1.0, END)
        self.emailBody.insert(1.0, 'From: '+message['From']+'\n')
        self.emailBody.insert(END, 'To: '+message['To']+'\n')
        if 'Cc' in message:
            self.emailBody.insert(END, 'Cc: '+message['Cc']+'\n')
        self.emailBody.insert(END, 'Subject: '+message['Subject']+'\n')
        if 'attachments' in message:
            for i in range(len(message['attachments'])):
                self.emailBody.insert(END, 'Attachment: '+message['attachments'][i]['filename']+'\n')
        self.emailBody.insert(END, '\n'+body)
        self.v_to = message['From']
        if 'Cc' in message:
            self.v_cc = message['Cc']
        else:
            self.v_cc = ''
        self.v_subject = message['Subject']
        self.v_msg = body
        self.v_date = message['Date']
        self.v_message_id = message['Message-Id']

    #
    # -- printInboxMessage
    # print self.selected_message from inbox (POP3 or IMAP) folder
    #

    def printInboxMessage(self):
        self.statusLabel['text']='fetching message...'
        if self.protocol == 'IMAP':
            mailer = lib.asafonov_imap.imapConnector(self.program_folder)
        else:
            mailer = lib.asafonov_pop3.pop3Connector(self.program_folder)
        mailer.host = self.pop3host
        mailer.port = self.pop3port
        mailer.login = self.login
        mailer.password = self.password
        mailer.is_ssl = int(self.is_ssl)
        message = mailer.getMessage(self.selected_message)
        self.printMessage(message)
        self.statusLabel['text']=''
        if self.colors['toolbar']=='1':
            self.replyButton['state'] = NORMAL
            self.deleteButton['state'] = NORMAL

    def onComposeButton(self):
        spam = Tk()
        spam.title('Compose message')
        onSpam = composeForm(master=spam, v_to='', v_subject='', v_msg='', v_cc='', program_folder=self.program_folder)
        onSpam = mainloop()

    def onReplyButton(self):
        spam = Tk()
        spam.title('Compose message')
        lines = self.v_msg.split('\n')
        v_msg = ''
        for i in range(len(lines)):
            v_msg += '> '+lines[i]+'\n'
        onSpam = composeForm(master=spam, v_to=self.v_to, v_subject='Re: '+self.v_subject, v_msg='\n\nOn '+self.v_date+' you wrote:\n\n'+v_msg, v_cc = self.v_cc, program_folder=self.program_folder)
        onSpam = mainloop()

    def deleteMessage(self):
        if self.colors['toolbar']=='1':
            self.replyButton['state'] = DISABLED
            self.deleteButton['state'] = DISABLED
        self.statusLabel['text'] = 'deleting message...'
        if self.protocol == 'IMAP':
            mailer = lib.asafonov_imap.imapConnector(self.program_folder)
        else:
            mailer = lib.asafonov_pop3.pop3Connector(self.program_folder)
        mailer.host = self.pop3host
        mailer.port = self.pop3port
        mailer.login = self.login
        mailer.password = self.password
        mailer.is_ssl = int(self.is_ssl)
        mailer.deleteMessage(self.selected_message)
        self.statusLabel['text'] = ''
        self.emailBody.delete('1.0', END)
        self.selected_message=0
        self.v_to = ''
        self.v_cc = ''
        self.v_subject = ''
        self.v_msg = ''
        self.v_message_id = ''
        self.printMessageList()

    def onDeleteButton(self):
        if self.colors['threading'] == '1':
            threading.Thread(target=self.deleteMessage).start()
        else:
            self.deleteMessage()

    def getColors(self):
        self.colors = {}
        f = open(self.program_folder+'config/colors')
        lines = f.read().split('\n')
        f.close()
        for i in range(len(lines)):
            tmp = lines[i].split(':')
            if len(tmp)>1:
                self.colors[tmp[0]] = tmp[1]

    def __init__(self, master=None, program_folder=''):
        Frame.__init__(self, master)
        self.master = master
        self.pack()
        self.program_folder = program_folder
        if os.path.exists(program_folder+'cache'):
            shutil.rmtree(program_folder+'cache')
        os.makedirs(program_folder+'cache')
        if not os.path.exists(program_folder+'sent'):
            os.makedirs(program_folder+'sent')
        self.getColors()
        self.createWidgets(master)



class composeForm(Frame):

    def createWidgets(self, master, v_to, v_subject, v_msg, v_cc):
        f = open(self.program_folder+'config/signature')
        v_msg = '\n\n'+f.read()+v_msg
        f.close()
        self.labelTo=Label(self, text='To: ')
        self.labelTo.grid(row=0, column=0)
        self.inputTo = ttk.Entry(self, width=100)
        self.inputTo.grid(row=0, column=1, sticky=N+E+W)
        self.inputTo.insert(0, v_to)
        self.labelSubject =Label(self, text='Subject: ')
        self.labelSubject.grid(row=1, column=0)
        self.inputSubject = ttk.Entry(self, width=100)
        self.inputSubject.grid(row=1, column=1, sticky=N+E+W)
        self.inputSubject.insert(0, v_subject)
        self.labelCc=Label(self, text='Cc: ')
        self.labelCc.grid(row=2, column=0)
        self.inputCc = ttk.Entry(self, width=100)
        self.inputCc.grid(row=2, column=1, sticky=N+E+W)
        self.inputCc.insert(0, v_cc)
        self.labelBody = Label(self, text='Message: ')
        self.labelBody.grid(row=4, column=0)
        self.inputBody = Text(self, width=100, height=30)
        self.inputBody['background'] = '#ffffff'
        self.inputBody.grid(row=4, column=1, sticky=N+E+W)
        self.inputBody.insert('1.0', v_msg)
        self.labelAttach=Label(self, text='Attachments: ')
        self.labelAttach.grid(row=5, column=0)
        self.inputAttach = ttk.Entry(self, width=100)
        self.inputAttach.grid(row=5, column=1, sticky=N+E+W)
        self.buttonFrame = ttk.Frame(self)
        self.buttonFrame.grid(row=6, column=0, columnspan=2, sticky=N+E+W)
        self.sendButton = ttk.Button(self.buttonFrame, text='Send', command=self.sendMessage)
        self.sendButton.grid(row=0, column=0)

    def sendMessage(self):
        mailer = lib.asafonov_smtp.smtpConnector(self.program_folder)
        f = open(self.program_folder+'config/access')
        lines = f.read().split('\n')
        f.close()
        mailer.host = lines[5]
        mailer.port = lines[6]
        mailer.login = lines[2]
        mailer.password = lines[3]
        mailer.is_ssl = int(lines[4])
        mailer.from_email=lines[7]
        v_attach = self.inputAttach.get()
        attach_dir = ''
        filenames = []
        if v_attach!='':
            attach_dir = self.program_folder+'tmp/attach'
            os.makedirs(attach_dir)
            import shutil
            spam = v_attach.split(';')
            for i in range(len(spam)):
                shutil.copy(spam[i].strip(), attach_dir)
            filenames = os.listdir(attach_dir)
        v_to = self.inputTo.get()
        v_cc = self.inputCc.get()
        v_subject = self.inputSubject.get()
        v_msg = self.inputBody.get('1.0', END)
        v_msg = v_msg.replace('\n', '<br>')
        mailer.sendMessage(v_to, v_subject, v_msg, filenames, attach_dir, v_cc)
        self.master.withdraw()

    def __init__(self, master=None, v_to='', v_subject='', v_msg='', v_cc='', program_folder=''):
        Frame.__init__(self, master)
        self.master = master
        self.pack()
        self.program_folder = program_folder
        self.createWidgets(master, v_to, v_subject, v_msg, v_cc)

root = Tk()
root.title('Stormbringer')
if len(sys.argv)>1:
    program_folder = sys.argv[1]
else:
    program_folder = ''
app = emailGui(master=root, program_folder=program_folder)
root.bind('<Key>', app.onKeyPressed)
root.config(menu=app.createMenu())
app.mainloop()
root.destroy()