#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Feb 23, 2012

@author: cda
'''
import smtplib 
import logging

class SmtpConnector(object):
    
    def __init__(self, smtp):
        self.log = logging.getLogger('SmtpConnectorFactory')
        self.smtp = smtp


    def _login(self, username, password):
        self.log.info('logging in [%s]' % username)
        self.smtp.ehlo()
        self.smtp.starttls()
        self.smtp.ehlo()
        self.smtp.login(username, password)
        return self

    def logout(self):
        self.smtp.close()
        
    def email(self, email):
        self.log.info('delivering mail [%(Subject)s] from [%(FROM)s] to [%(TO)s]...' % email)
        self.smtp.sendmail(email['FROM'], email['TO'], email.as_string())

    @staticmethod
    def connector_for(server):
        log = logging.getLogger('SmtpConnectorFactory')
        log.info('connecting to server [%s]...' % server)
        return SmtpConnector(smtplib.SMTP(server, 587))
