# -*- coding: utf-8 -*-

class emailThreader:

    email_list = []
    email_thread = []
    
    def getEmailThreads(self):
        self.email_thread = []
        for i in range(len(self.email_list)):
            spam = {}
            # email number. I'm not sure it needed at all
            spam['num'] = i+1
            spam['patricipants'] = []
            spam['participants'].append(self.email_list[i]['From'])
            spam['participants'].append(self.email_list[i]['To'])
            if 'Cc' in self.email_list[i]:
                spam['participants'].append(self.email_list[i]['Cc'])
            spam['participants'].sort()
            spam['subject'] = self.email_list[i]['Subject'].lower().replace(' ', '')
            spam['subject'] = re.sub('re[^:]*:','', spam['subject'])
            spam['subject'] = re.sub('fw[^:]*:','', spam['subject'])
            spam['parent'] = 0
            j = i-1
            while j>=0:
                if self.email_thread[i]['subject']==spam['subject'] and self.email_thread[i]['participants']==spam['participants']:
                    spam['parent'] = i+1
