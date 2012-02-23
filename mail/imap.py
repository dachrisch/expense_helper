#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Feb 23, 2012

@author: cda
'''
import logging
import email
from email.header import decode_header
import imaplib

class ImapConnector(object):
    def __init__(self, imap):
        self.imap = imap
        self.log = logging.getLogger('ImapConnector')
        
    def _login(self, username, password):
        self.log.info('logging in [%s]' % username)
        self.imap.login(username, password)
        return self
        
    def filter_inboxes(self, criteria):
        status, available_inboxes = self.imap.list()
        assert status == 'OK', status
        filtered_inboxes = filter(
                                    criteria, 
                                    map(lambda inbox: inbox.replace('(\\HasNoChildren) "/" ', ''), available_inboxes)
                                    )
        self.log.debug('filtered %s from available inboxes: %s' % (filtered_inboxes, available_inboxes))
        return filtered_inboxes
    
    def __search_uids(self):
        response, uids_data = self.imap.uid('search', None, 'ALL')
        assert response == 'OK', response
        uids = uids_data[0].split()
        return uids

    def __fetch_emails(self, uids):
        for uid in uids:
            response, rfc822_mail = self.imap.uid('fetch', uid, '(BODY[HEADER.FIELDS (DATE SUBJECT FROM Message-ID)])')
            assert response == 'OK', response
            parsed_email = email.message_from_string(rfc822_mail[0][1])
            yield {
                   'Subject' : self.__remove_encoding(parsed_email['Subject']),
                   'DATE' : parsed_email['DATE'],
                   'FROM' : parsed_email['FROM'],
                   'Message-ID' : parsed_email['Message-ID'],
                   }
            
    def __remove_encoding(self, text):
        texts_with_charsets = decode_header(text)
        decoded_text = ''.join([ unicode(t[0], t[1] or 'ASCII') for t in texts_with_charsets ])
        return decoded_text.encode('utf-8')

    def read_from(self, inbox):
        self.imap.select(inbox, readonly = True)

        uids = self.__search_uids()
        
        self.log.info('reading [%d] mails from [%s]' % (len(uids), inbox))        
        self.log.debug('processing %s' % (uids))
        
        emails = self.__fetch_emails(uids)
        return emails
    
    def close(self):
        self.imap.close()

def connector_for(server):
    log = logging.getLogger('ImapConnectorFactory')
    log.info('connecting to server [%s]...' % server)
    return ImapConnector(imaplib.IMAP4_SSL(server, 993))
