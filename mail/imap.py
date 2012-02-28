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
import re
import shlex
from contextlib import contextmanager

class ImapConnector(object):
    def __init__(self, imap):
        self.imap = imap
        self.log = logging.getLogger('ImapConnector')
        
    @contextmanager
    def create_connection(self, username, password):
        self.__login(username, password)
        try:
            yield self
        finally:
            self._close()

    def __login(self, username, password):
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
    
    def __search_uids(self, gmail_query):
        response, uids_data = self.imap.uid('search', None, '(X-GM-RAW "%s")' % gmail_query)
        assert response == 'OK', response
        uids = uids_data[0].split()
        return uids

    def __fetch_emails(self, uids, fetch_options):
        for uid in uids:
            response, rfc822_mail = self.imap.uid('fetch', uid, fetch_options)
            assert response == 'OK', response
            parsed_email = email.message_from_string(rfc822_mail[0][1])
            self.__store_uid(parsed_email, uid)
            self.__restore_subject(parsed_email)
            self.__fetch_labels(parsed_email)
            yield parsed_email

    def __store_uid(self, email, uid):
        email['UID'] = uid

    def __restore_subject(self, email):
        if 'Subject' in email.keys():
            email.replace_header('Subject', self.__remove_encoding(email['Subject']))

    def __fetch_labels(self, email):
        assert email['UID']
        response, label_data = self.imap.uid('FETCH', email['UID'], '(X-GM-LABELS)')
        assert response == 'OK', response
        label_pattern = re.compile('\d+ \(X-GM-LABELS \((?P<labels>.*)\) UID \d+\)')
        m = label_pattern.match(label_data[0])
        if m:
            email['labels'] = shlex.split(m.group('labels'))
        
    def __remove_encoding(self, text):
        texts_with_charsets = decode_header(text)
        decoded_text = ''.join([ unicode(t[0], t[1] or 'ASCII') for t in texts_with_charsets ])
        return decoded_text.encode('utf-8')

    def read_from(self, inbox, gmail_query, fetch_options = '(BODY[HEADER.FIELDS (DATE SUBJECT FROM)])'):
        self.imap.select(inbox, readonly = False)

        uids = self.__search_uids(gmail_query)
        
        self.log.debug('reading [%d] mails from [%s]' % (len(uids), inbox))        
        self.log.debug('processing %s' % (uids))
        
        emails = self.__fetch_emails(uids, fetch_options)
        return emails
    
    def copy_to_inbox(self, email, inbox):
        self.log.debug('%s %s %s' % ('COPY', email['UID'], inbox))
        response, data = self.imap.uid('COPY', email['UID'], inbox)
        assert response == 'OK', response
    
    def _close(self):
        self.log.info('closing imap connection.')
        self.imap.close()

    @staticmethod
    def connector_for(server):
        log = logging.getLogger('ImapConnectorFactory')
        log.info('connecting to server [%s]...' % server)
        return ImapConnector(imaplib.IMAP4_SSL(server, 993))
