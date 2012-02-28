#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Feb 23, 2012

@author: cda
'''
import logging.config
import sys
from os import path
from mail.imap import ImapConnector
from handler.category import EmailCategorizerFactory
from handler.filter import EmailFilterHandler, EmailCleanup
from mail.smtp import SmtpConnector
from ConfigParser import ConfigParser
from optparse import OptionParser
from config import ExpenseConfigParser
from handler.provider import CommandlinePasswordProvier,\
    CommandlineConfirmationProvier

def fetch_expense_inboxes(connection, config_provider):
    return connection.filter_inboxes(lambda inbox: inbox.startswith('"' + config_provider.expense_label))

def _checked_load_logging_config(config_path):
    expanded_config_path = path.expanduser(config_path)
    if not path.exists(expanded_config_path):
        raise Exception("failed to locate a logging configuration at [%s]. please check the location" % expanded_config_path)
    logging.config.fileConfig(expanded_config_path)

def main():
    parser = OptionParser()
    parser.add_option("-i", "--ini-file", dest="ini_file",
                      help="read configuration from FILE (default: %default)", metavar="FILE", default="expense.ini")
    parser.add_option("-v", "--verbose",
                      action="count", dest="verbose",
                      help="print status messages to stdout more verbose", default=1)
    parser.add_option("-c", "--create-default-config", dest="create_default_config", action="store_true",
                      help="create a default config file", default=False)

    (options, args) = parser.parse_args()
    if options.verbose > 1:
        _checked_load_logging_config("~/.python/logging_debug.conf")
    elif options.verbose:
        _checked_load_logging_config("~/.python/logging.conf")
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.WARN)
        
    config_parser = ExpenseConfigParser(ConfigParser(), options.ini_file)
    if options.create_default_config:
        config_parser.store()
    else:
        ExpenseHelper(config_provider = config_parser.load()).run()
    
class ExpenseHelper(object):
    def __init__(
                    self, 
                    config_provider,
                    imap_factory = ImapConnector.connector_for, 
                    password_provider = CommandlinePasswordProvier.password, 
                    confirmation_provider = CommandlineConfirmationProvier.confirm, 
                    smtp_factory = SmtpConnector.connector_for
                ):
        self.imap_factory = imap_factory
        self.password_provider = password_provider
        self.confirmation_provider = confirmation_provider
        self.smtp_factory = smtp_factory
        self.config_provider = config_provider

    def run(self):
    
        log = logging.getLogger('ExpenseHelper')
        
        username = self.config_provider.username
        password = self.password_provider(username)
        with self.imap_factory(self.config_provider.imap_server).create_connection(username, password) as imap_connection:
        
            email_categorizer = EmailCategorizerFactory.create(self.config_provider)
        
            expense_inboxes = fetch_expense_inboxes(imap_connection, self.config_provider)
        
            categorized_emails = []
            for inbox in expense_inboxes:
                emails = imap_connection.read_from(inbox, '(RFC822)')
                categorized_emails.extend(email_categorizer.categorize(inbox, emails))
        
            log.info('categorized [%d] emails...now filtering...' % (len(categorized_emails)))
            
            forward_candidates = map(EmailCleanup(self.config_provider.sender, self.config_provider.receiver).prepare_outbound, 
                                     filter(EmailFilterHandler(self.config_provider).filter_candidate, categorized_emails))
    
            answer = self.confirmation_provider(forward_candidates)
            if answer:
                with self.smtp_factory(self.config_provider.smtp_server).create_connection(username, password) as smtp_connection:
                    for email in forward_candidates:
                        imap_connection.copy_to_inbox(email, '[Gmail]/Sent Mail')
                        smtp_connection.email(email)
                        imap_connection.copy_to_inbox(email, self.config_provider.delivered_label)
            else:
                log.warn('doing nothing. bye')

if __name__ == '__main__':
    main()
