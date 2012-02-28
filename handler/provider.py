#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Feb 28, 2012

@author: cda
'''
import logging
import getpass
class CommandlinePasswordProvier(object):
    @staticmethod
    def password(username):
        return getpass.getpass('password for [%s]: ' % username)

class CommandlineConfirmationProvier(object):
    def __init__(self):
        self.log = logging.getLogger('CommandlineConfirmationProvier')
    def confirm(self, emails):
        if len(emails):
            self.log.warn('about to forward [%d] emails to [%s]:' % (len(emails), emails[0]['To']))
            self.log.info('\n'.join(map(lambda x: x['Subject'], emails)))
            return raw_input("continue?: ").lower() in ('j', 'y')
        else:
            self.log.warn('all mails rejected.')
            return False
