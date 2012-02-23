#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Feb 23, 2012

@author: cda
'''

import re
import logging

def extract_nested_inbox(inbox):
    return inbox.split('/')[-1]
    
class EmailCategorizerFactory(object):
    @staticmethod
    def create(connection):
        return EmailCategorizer(CostCenterMatcher(connection))

class EmailCategorizer(object):
    def __init__(self, costcenter_matcher):
        self.log = logging.getLogger('EmailCategorizer')
        self.costcenter_matcher = costcenter_matcher
    def categorize(self, inbox, emails):
        return [self.__categorize(inbox, email) for email in emails]

    def __categorize(self, inbox, email):
        subject = email['Subject']
        categorized = {
                'payment_type' : extract_nested_inbox(inbox),
                'order_date' : self.__parse_date(email['DATE']),
                'provider' : self.__parse_provider(email),
                'cost_center' : self.costcenter_matcher.costcenter_for(email),
                'subject' : subject
                }
        self.log.info('categorized [%s] as: %s' % (subject, categorized))
        return categorized
    
    def __parse_date(self, send_date_rfc_2822):
        import time
        from email.utils import parsedate 
        from datetime import date
    
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
    def __init__(self, connection):
        self.log = logging.getLogger('CostCenterMatcher')
        cost_center_inboxes = connection.filter_inboxes(lambda inbox: inbox.startswith('"costcenter/'))
        self.log.info('pre determining messages for [%d] cost centers...' % len(cost_center_inboxes))
        self.costcenters = {}
        for inbox in cost_center_inboxes:
            emails = connection.read_from(inbox)
            for email in emails:
                self.costcenters[email['Message-ID']] = extract_nested_inbox(inbox)
        self.log.debug('determined cost centers: %s' % self.costcenters)

    def costcenter_for(self, email):
        m_id = email['Message-ID']
        if m_id in self.costcenters.keys():
            return self.costcenters[m_id]
        else:
            raise Exception('message [%(Subject)s] with ID [%(Message-ID)s] has no cost center assigned' % email)
