# -*- coding: utf-8 -*-
import lib.asafonov_email_parser
import lib.asafonov_user_login
import os

def readFolder(folder):
    if os.path.exists(folder):
        folder_list = os.listdir(folder)
    else:
        folder_list = []
    return folder_list

def getUserSentFolder(program_folder=''):
    user_info = lib.asafonov_user_login.getUserInfo()
    return program_folder+'sent/'+user_info['from_email']

def getUserArchiveFolder(program_folder=''):
    user_info = lib.asafonov_user_login.getUserInfo(program_folder)
    return program_folder+'archive/'+user_info['from_email']

def saveArchiveMessage(message_id, program_folder=''):
    user_info = lib.asafonov_user_login.getUserInfo(program_folder)
    letter_file = program_folder+'archive/'+user_info['from_email']
    if not os.path.exists(letter_file):
        os.makedirs(letter_file)
    letter_file+='/'+message_id
    import shutil
    shutil.copy(program_folder+'cache/'+message_id+'.eml', letter_file+'.eml')
    if os.path.exists(program_folder+'cache/'+message_id):
        shutil.copytree(program_folder+'cache/'+message_id, letter_file)
    return '2'

def saveSentMessage(message_path, program_folder=''):
    import shutil
    archive_folder = getUserArchiveFolder(program_folder)
    sent_folder = getUserSentFolder(program_folder)
    message_id = message_path.split('/')[1]
    shutil.copy(sent_folder+'/'+message_path, archive_folder+'/'+message_id)
    return '2'

def readSentFolder(program_folder):
    user_sent_folder = getUserSentFolder(program_folder)
    out = []
    if os.path.exists(user_sent_folder):
        out = readFolder(user_sent_folder)
    return out

def readEmailFolder(email, program_folder=''):
    return readFolder(getUserSentFolder(program_folder)+'/'+email)

def printArchiveMessage(path, program_folder=''):
    message = lib.asafonov_email_parser.getMessageFromCache(0, getUserArchiveFolder(program_folder)+'/'+path)
    return printMessage(message)

def getArchiveFolderItems(program_folder=''):
    user_archive_folder = getUserArchiveFolder(program_folder)
    spam =  readFolder(user_archive_folder)
    out = []
    for i in range(len(spam)):
        if os.path.isfile(user_archive_folder+'/'+spam[i]):
            out.append(lib.asafonov_email_parser.getMessageFromCache(0, user_archive_folder+'/'+spam[i]))
    return out

def removeArchiveMessage(message_id, program_folder=''):
    os.remove(getUserArchiveFolder(program_folder)+'/'+message_id)

def removeSentMessage(message_path, program_folder=''):
    os.remove(getUserSentFolder(program_folder)+'/'+message_path)
