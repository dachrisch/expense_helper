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

class ConfirmationProvier(object):
    @staticmethod
    def from_commandline(emails):
        log = logging.getLogger('CommandlineConfirmationProvier')
        accepting = ('j', 'y')
        if len(emails):
            log.warn('about to forward [%d] emails to [%s]:' % (len(emails), emails[0]['To']))
            log.info('\n'.join(map(lambda x: x['Subject'], emails)))
            return raw_input("%s to continue or any other key to abort: " % str(accepting)).lower() in accepting
        else:
            log.warn('all mails rejected.')
            return False

    @staticmethod
    def yes(emails):
        return len(emails)
