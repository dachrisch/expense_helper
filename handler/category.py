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
    def create(config_provider):
        return EmailCategorizer(CostCenterMatcher(config_provider))

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
                'Subject' : email['Subject']
                }
        self.log.info('categorized [%(Subject)s] as: [%(costcenter)s %(payment_type)s %(provider)s %(order_date)s]' % (email['categorized']))
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
    def __init__(self, config_provider):
        self.log = logging.getLogger('CostCenterMatcher')
        self.costcenter_inbox = config_provider.costcenter_label

    def costcenter_for(self, email):
        labels = email['labels']
        costcenter_labels = map(lambda label: extract_nested_inbox(label), filter(lambda label: label.startswith('%s/' % self.costcenter_inbox), labels))
        if not costcenter_labels:
            raise Exception('mail has no costcenter [%s/<costcenter>] assigned, cannot process: %s' % (self.costcenter_inbox, email))
        if len(costcenter_labels) > 1:
            raise Exception('only one costcenter assignment allowed, but found [%d]: %s' % (len(costcenter_labels), costcenter_labels))
        return costcenter_labels[0]

