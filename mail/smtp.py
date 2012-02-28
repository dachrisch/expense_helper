#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Feb 23, 2012

@author: cda
'''
import smtplib 
import logging
from contextlib import contextmanager

class SmtpConnector(object):
    
    def __init__(self, smtp):
        self.log = logging.getLogger('SmtpConnector')
        self.smtp = smtp

    @contextmanager
    def create_connection(self, username, password):
        try:
            yield self.__login(username, password)
        finally:
            self._close()

    def __login(self, username, password):
        self.log.info('logging in [%s]' % username)
        self.smtp.ehlo()
        self.smtp.starttls()
        self.smtp.ehlo()
        self.smtp.login(username, password)
        return self

    def _close(self):
        self.log.info('closing smtp connection.')
        self.smtp.quit()
        
    def email(self, email):
        self.log.info('delivering mail [%(Subject)s]...' % email)
        self.log.debug('sending [%d] bytes from [%s] to [%s]...' % (len(email.as_string()), email['From'], email['To']))
        self.smtp.sendmail(email['From'], email['To'], email.as_string())

    @staticmethod
    def connector_for(server):
        log = logging.getLogger('SmtpConnectorFactory')
        log.info('connecting to server [%s]...' % server)
        return SmtpConnector(smtplib.SMTP(server, 587))
