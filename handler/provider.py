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
    @staticmethod
    def confirm(emails):
        log = logging.getLogger('CommandlineConfirmationProvier')
        if len(emails):
            log.warn('about to forward [%d] emails to [%s]:' % (len(emails), emails[0]['To']))
            log.info('\n'.join(map(lambda x: x['Subject'], emails)))
            return raw_input("continue?: ").lower() in ('j', 'y')
        else:
            log.warn('all mails rejected.')
            return False
