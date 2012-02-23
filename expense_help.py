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
from category import EmailCategorizerFactory

def fetch_expense_inboxes(connection):
    return connection.filter_inboxes(lambda inbox: inbox.startswith('"spesen/'))

def main():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    username = 'christian.daehn@it-agile.de'
    password = getpass.getpass('password for [%s]: ' % username)
    connection = connector_for('imap.googlemail.com')._login(username, password)
    
    email_categorizer = EmailCategorizerFactory.create(connection)

    expense_inboxes = fetch_expense_inboxes(connection)
    
    for inbox in expense_inboxes:
        emails = connection.read_from(inbox)
        email_categorizer.categorize(inbox, emails)


    connection.close()


if __name__ == '__main__':
    main()