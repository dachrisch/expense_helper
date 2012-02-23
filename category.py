#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Feb 23, 2012

@author: cda
'''

from email.header import decode_header
import re
import logging

class EmailCategorizer(object):
    def __init__(self):
        self.log = logging.getLogger('EmailCategorizer')
    def categorize(self, inbox, emails):
        return [self.__categorize(inbox, email) for email in emails]

    def __categorize(self, inbox, email):
        subject = self.__remove_encoding(email['Subject'])
        categorized = {
                'payment_type' : self.__parse_payment_type(inbox),
                'order_date' : self.__parse_date(email['DATE']),
                'provider' : self.__parse_provider(email),
                'cost_center' : '?',
                'subject' : subject
                }
        self.log.info('categorized [%s] as: %s' % (subject, categorized))
        return categorized
    def __remove_encoding(self, text):
        texts_with_charsets = decode_header(text)
        decoded_text = ''.join([ unicode(t[0], t[1] or 'ASCII') for t in texts_with_charsets ])
        return decoded_text.encode('utf-8')
    
    def __parse_date(self, send_date_rfc_2822):
        import time
        from email.utils import parsedate 
        from datetime import date
    
        date_tuple = parsedate(send_date_rfc_2822)
        timestamp = time.mktime(date_tuple)
        send_date = date.fromtimestamp(timestamp)
    
        send_date_german = send_date.strftime('%d.%m.%Y') 
    
        return send_date_german
    
    def __parse_payment_type(self, inbox):
        return inbox.replace('spesen/', '')
        
    def __parse_provider(self, email):
        email_pattern = re.compile('([-+.a-zA-Z0-9]{1,64}@(?P<domain>[-.a-zA-Z0-9]{1,64})\.[-.a-zA-Z0-9]{2,6})')
        m = email_pattern.search(email['FROM'])
        if m:
            self.log.debug('parsed [%s] from [%s]' % (m.groups(), email['FROM']))
            return m.group('domain')
        return 'UNKNOWN'

