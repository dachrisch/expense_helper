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
from os import path
from mail.imap import ImapConnector
from category import EmailCategorizerFactory
from mail.smtp import SmtpConnector

def fetch_expense_inboxes(connection):
    return connection.filter_inboxes(lambda inbox: inbox.startswith('"spesen/'))

def _checked_load_logging_config(config_path):
    expanded_config_path = path.expanduser(config_path)
    if not path.exists(expanded_config_path):
        raise Exception("failed to locate a logging configuration at [%s]. please check the location" % expanded_config_path)
    logging.config.fileConfig(expanded_config_path)

class CommandlinePasswordProvier(object):
    @staticmethod
    def password(username):
        return getpass.getpass('password for [%s]: ' % username)

class CommandlineConfirmationProvier(object):
    @staticmethod
    def confirm(emails):
        log = logging.getLogger('CommandlineConfirmationProvier')
        log.warn('about to forward [%d] emails:' % len(emails))
        log.info('\n'.join(map(lambda x: x['Subject'], emails)))
        return raw_input("continue?: ")

def main():
    ExpenseHelper().run()

class ExpenseHelper(object):
    def __init__(self, imap_factory = ImapConnector.connector_for, password_provider = CommandlinePasswordProvier.password, confirmation_provider = CommandlineConfirmationProvier.confirm, smtp_factory = SmtpConnector.connector_for):
        self.imap_factory = imap_factory
        self.password_provider = password_provider
        self.confirmation_provider = confirmation_provider
        self.smtp_factory = smtp_factory
    def run(self):
        log = logging.getLogger('main')
    
        username = 'christian.daehn@it-agile.de'
        password = self.password_provider(username)
        imap_connection = self.imap_factory('imap.googlemail.com')._login(username, password)
        
        email_categorizer = EmailCategorizerFactory.create(imap_connection)
    
        expense_inboxes = fetch_expense_inboxes(imap_connection)
    
        categorized_emails = []
        for inbox in expense_inboxes:
            emails = imap_connection.read_from(inbox, '(RFC822)')
            categorized_emails.extend(email_categorizer.categorize(inbox, emails))
    
        imap_connection.close()
        log.info('categorized [%d] emails...now forwarding...' % len(categorized_emails))
        
        forward_candidates = []
        for categorized_email in categorized_emails:
            if 'it-agile' == categorized_email['categorized']['provider']:
                log.warn('skipping own mail [%s]' % categorized_email['Subject'])
                continue
            categorized_email.replace_header('FROM', 'christian.daehn@it-agile.de')
            categorized_email.replace_header('TO', 'christian.daehn+moneypennytest@it-agile.de')
            categorized = categorized_email['categorized']
            categorized['intro'] = 'Fwd:'
            categorized['outro'] = '(was: %s)' % categorized_email['Subject']
            categorized_email.replace_header('Subject', '%(intro)s %(costcenter)s %(payment_type)s %(provider)s %(order_date)s %(outro)s' % categorized)
            del categorized_email['categorized']
            forward_candidates.append(categorized_email)
        
        answer = self.confirmation_provider(forward_candidates)
        if answer.lower() in ('j', 'y'):
            smtp = self.smtp_factory('smtp.googlemail.com')._login(username, password)
            for email in forward_candidates:
                smtp.email(email)
            smtp.logout()
        else:
            log.warn('doing nothing. bye')

if __name__ == '__main__':
    try:
        _checked_load_logging_config("~/.python/logging.conf")
    except:
        logging.basicConfig(stream=sys.stdout, level=logging.WARN)
    main()
