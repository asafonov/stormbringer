# -*- coding: utf-8 -*-

def getUserInfo(program_folder = ''):
    user_info = {}
    f = open(program_folder+'config/access')
    content = f.read()
    f.close()
    lines = content.split('\n')
    user_info['from_email'] = lines[7]
    return user_info
