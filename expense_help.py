#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Feb 23, 2012

@author: cda
'''
import getpass
import logging
import logging.config
import sys
from mail.imap import connector_for
from category import EmailCategorizer

    
def main():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    connection = connector_for('imap.googlemail.com')
    
    username = 'christian.daehn@it-agile.de'
    password = getpass.getpass('password for [%s]: ' % username)
    connection._login(username, password)
    
    expense_inboxes = connection.filter_inboxes(lambda inbox: inbox.startswith('"spesen/'))
    
    for inbox in expense_inboxes:
        emails = connection.read_from(inbox)
        EmailCategorizer().categorize(inbox, emails)

    connection.close()


if __name__ == '__main__':
    main()