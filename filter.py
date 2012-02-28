#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Feb 28, 2012

@author: cda
'''
import logging
class EmailFilter(object):
    def __init__(self):
        self.log = logging.getLogger('EmailFilter')
    def accept(self, email):
        pass
    def _log(self, email, result):
        if result:
            self.log.debug('filter [%s] passed - accepting email [%s]' % (self, email['Subject']))
        else:
            self.log.info('filter [%s] failed - rejecting email [%s]' % (self, email['Subject']))
        return result

class RejectingProviderFilter(EmailFilter):
    def __init__(self, provider_to_reject):
        EmailFilter.__init__(self)
        self._provider = 'it-agile'
    def accept(self, email):
        return self._log(email, self._provider != email['categorized']['provider'])
    def __str__(self):
        return 'filter checking provider not to be [%s]' % self._provider
        
class NotDeliveredFilter(EmailFilter):
    def __init__(self):
        EmailFilter.__init__(self)
        self._label = 'delivered'
    def accept(self, email):
        return self._log(email, self._label not in email['labels'])
    def __str__(self):
        return 'filter checking labels not to contain [%s]' % self._label
    
class HasAttachmentFilter(EmailFilter):
    def __init__(self):
        EmailFilter.__init__(self)
    def accept(self,email):
        return self._log(email, any(map(HasAttachmentFilter.has_attachment, email.walk())))
    def __str__(self):
        return 'filter checking email to contain attachment'
    @staticmethod
    def has_attachment(part):
        cd = part.get('Content-Disposition')
        return cd is not None and cd.startswith('attachment') 
        
class EmailFilterHandler(object):
    def __init__(self, config_provider):
        self.log = logging.getLogger('EmailFilterHandler')
        self.config_provider = config_provider
        self.__add_filter()
    def __add_filter(self):
        self._filters = (NotDeliveredFilter(), RejectingProviderFilter('it-agile'), HasAttachmentFilter())
        
    def _accept(self, email):
        accept = True
        for _filter in self._filters:
            accept &= _filter.accept(email)
        return accept
    def filter_candidates(self, emails):
        candidate_emails = []
        for email in filter(self._accept, emails):
            self.__email_from(email, self.config_provider.get('account', 'username'))
            self.__send_to(email, self.config_provider.get('account', 'destination'))
            self.__create_subject(email)
            self.__cleanup_email(email)
            candidate_emails.append(email)
        return candidate_emails
    def __create_subject(self, email):
        categorized = email['categorized']
        categorized['intro'] = 'Fwd:'
        categorized['outro'] = '(was: %s)' % email['Subject']
        email.replace_header('Subject', '%(intro)s %(costcenter)s %(payment_type)s %(provider)s %(order_date)s %(outro)s' % categorized)
    def __cleanup_email(self, email):
        del email['categorized']
        del email['labels']
    def __send_to(self, email, to):
        if 'TO' in email.keys():
            email.replace_header('TO', to)
        else:
            email.add_header('TO', to)
    def __email_from(self, email, _from):
        email.replace_header('FROM', _from)
