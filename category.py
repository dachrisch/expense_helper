#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Feb 23, 2012

@author: cda
'''

import re
import logging
import time
from email.utils import parsedate 
from datetime import date

def extract_nested_inbox(inbox):
    return inbox.split('/')[-1].replace('"', '').replace(' ', '')
    
class EmailCategorizerFactory(object):
    @staticmethod
    def create(connection, config_provider):
        return EmailCategorizer(CostCenterMatcher(connection, config_provider))

class EmailCategorizer(object):
    def __init__(self, costcenter_matcher):
        self.log = logging.getLogger('EmailCategorizer')
        self.costcenter_matcher = costcenter_matcher
    def categorize(self, inbox, emails):
        return [self.__categorize(inbox, email) for email in emails]

    def __categorize(self, inbox, email):
        email['categorized'] = {
                'payment_type' : extract_nested_inbox(inbox),
                'order_date' : self.__parse_date(email['DATE']),
                'provider' : self.__parse_provider(email),
                'costcenter' : self.costcenter_matcher.costcenter_for(email),
                'email' : email
                }
        self.log.info('categorized [%(Subject)s] as: %(categorized)s' % (email))
        return email
    
    def __parse_date(self, send_date_rfc_2822):
        date_tuple = parsedate(send_date_rfc_2822)
        timestamp = time.mktime(date_tuple)
        send_date = date.fromtimestamp(timestamp)
    
        send_date_german = send_date.strftime('%d.%m.%Y') 
    
        return send_date_german
    
    def __parse_provider(self, email):
        email_pattern = re.compile('([-+.a-zA-Z0-9]{1,64}@(?P<domain>[-.a-zA-Z0-9]{1,64})\.[-.a-zA-Z0-9]{2,6})')
        m = email_pattern.search(email['FROM'])
        if m:
            self.log.debug('parsed [%s] from [%s]' % (m.groups(), email['FROM']))
            return m.group('domain')
        return 'UNKNOWN'

class CostCenterMatcher(object):
    def __init__(self, connection, config_provider):
        self.log = logging.getLogger('CostCenterMatcher')
        cost_center_inboxes = connection.filter_inboxes(lambda inbox: inbox.startswith(config_provider.get('labels', 'costcenter')))
        self.log.info('pre determining messages for [%d] cost centers...' % len(cost_center_inboxes))
        self.costcenters = {}
        for inbox in cost_center_inboxes:
            emails = connection.read_from(inbox, '(BODY[HEADER.FIELDS (Message-ID)])')
            for email in emails:
                self.log.debug('determining cost center for [%s]' % email)
                self.costcenters[email['Message-ID'].strip()] = extract_nested_inbox(inbox)
        self.log.debug('determined cost centers: %s' % self.costcenters)

    def costcenter_for(self, email):
        m_id = email['Message-ID'].strip()
        if m_id in self.costcenters.keys():
            return self.costcenters[m_id]
        else:
            msg = 'message [%(Subject)s] with ID [%(Message-ID)s] has no cost center assigned.' % email
            msg += ' Available cost message ids: %s' % '\n'.join(self.costcenters.keys())
            raise Exception(msg)

class EmailFilter(object):
    def __init__(self, config_provider):
        self.log = logging.getLogger('EmailForwarder')
        self.config_provider = config_provider
    def _accept(self, email):
        return 'it-agile' != email['categorized']['provider']
    def filter_candidates(self, emails):
        for email in emails:
            if not self._accept(email):
                self.log.warn('skipping own mail [%s]' % email['Subject'])
                return
            email.replace_header('FROM', self.config_provider.get('account', 'username'))
            email.replace_header('TO', self.config_provider.get('account', 'destination'))
            categorized = email['categorized']
            categorized['intro'] = 'Fwd:'
            categorized['outro'] = '(was: %s)' % email['Subject']
            email.replace_header('Subject', '%(intro)s %(costcenter)s %(payment_type)s %(provider)s %(order_date)s %(outro)s' % categorized)
            del email['categorized']
            yield email
