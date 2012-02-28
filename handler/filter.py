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
            self.log.debug('PASS - [%s] - accepting email [%s]' % (self, email['Subject']))
        else:
            self.log.info('FAIL - [%s] - rejecting email [%s]' % (self, email['Subject']))
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
        self._filters = (NotDeliveredFilter(), RejectingProviderFilter('it-agile'))
        
    def filter_candidate(self, email):
        accept = True
        for _filter in self._filters:
            accept &= _filter.accept(email)
        return accept

class EmailCleanup(object):
    def __init__(self, _from, to):
        self._from = _from
        self.to = to
    def __create_subject(self, email):
        categorized = email['categorized']
        categorized['intro'] = 'Fwd:'
        categorized['outro'] = '(was: %s)' % email['Subject']
        email.replace_header('Subject', '%(intro)s %(costcenter)s %(payment_type)s %(provider)s %(order_date)s %(outro)s' % categorized)
    def __cleanup_email(self, email):
        del email['categorized']
        del email['labels']
    def __send_to(self, email, to):
        if 'To' in email.keys():
            email.replace_header('To', to)
        else:
            email.add_header('To', to)
    def __email_from(self, email, _from):
        email.replace_header('From', _from)
    def prepare_outbound(self, email):
        self.__email_from(email, self._from)
        self.__send_to(email, self.to)
        self.__create_subject(email)
        self.__cleanup_email(email)
        return email