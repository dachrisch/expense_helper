#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Feb 23, 2012

@author: cda
'''
import getpass
import logging.config
import sys
from os import path
from mail.imap import ImapConnector
from category import EmailCategorizerFactory
from filter import EmailFilterHandler, EmailCleanup
from mail.smtp import SmtpConnector
import ConfigParser

def fetch_expense_inboxes(connection, config_provider):
    return connection.filter_inboxes(lambda inbox: inbox.startswith('"' + config_provider.get('labels', 'expense')))

def _checked_load_logging_config(config_path):
    expanded_config_path = path.expanduser(config_path)
    if not path.exists(expanded_config_path):
        raise Exception("failed to locate a logging configuration at [%s]. please check the location" % expanded_config_path)
    logging.config.fileConfig(expanded_config_path)

class CommandlinePasswordProvier(object):
    @staticmethod
    def password(username):
        return getpass.getpass('password for [%s]: ' % username)


def confirm(emails):
    log = logging.getLogger('CommandlineConfirmationProvier')
    if len(emails):
        log.warn('about to forward [%d] emails to [%s]:' % (len(emails), emails[0]['To']))
        log.info('\n'.join(map(lambda x: x['Subject'], emails)))
        return raw_input("continue?: ").lower() in ('j', 'y')
    else:
        log.warn('all mails rejected.')
        return False

def main():
    try:
        _checked_load_logging_config("~/.python/logging.conf")
    except:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    ExpenseHelper().run()
    
class ExpenseHelper(object):
    def __init__(
                    self, 
                    imap_factory = ImapConnector.connector_for, 
                    password_provider = CommandlinePasswordProvier.password, 
                    confirmation_provider = confirm, 
                    smtp_factory = SmtpConnector.connector_for,
                    config_provider = ConfigParser.ConfigParser()
                ):
        self.imap_factory = imap_factory
        self.password_provider = password_provider
        self.confirmation_provider = confirmation_provider
        self.smtp_factory = smtp_factory
        self.config_provider = config_provider

    def run(self):
        log = logging.getLogger('main')
        
        self.config_provider.read('expense.ini')
    
        username = self.config_provider.get('mail', 'username')
        password = self.password_provider(username)
        with self.imap_factory(self.config_provider.get('mail', 'imap_server')).create_connection(username, password) as imap_connection:
        
            email_categorizer = EmailCategorizerFactory.create(self.config_provider)
        
            expense_inboxes = fetch_expense_inboxes(imap_connection, self.config_provider)
        
            categorized_emails = []
            for inbox in expense_inboxes:
                emails = imap_connection.read_from(inbox, '(RFC822)')
                categorized_emails.extend(email_categorizer.categorize(inbox, emails))
        
            log.info('categorized [%d] emails...now filtering...' % (len(categorized_emails)))
            
            forward_candidates = map(EmailCleanup(self.config_provider.get('account', 'username'), self.config_provider.get('account', 'destination')).prepare_outbound, 
                                     filter(EmailFilterHandler(self.config_provider).filter_candidate, categorized_emails))
    
            answer = self.confirmation_provider(forward_candidates)
            if answer:
                with self.smtp_factory(self.config_provider.get('mail', 'smtp_server')).create_connection(username, password) as smtp_connection:
                    for email in forward_candidates:
                        smtp_connection.email(email)
                        imap_connection.add_label(email, 'delivered')
            else:
                log.warn('doing nothing. bye')

if __name__ == '__main__':
    main()
