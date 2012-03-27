#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Feb 23, 2012

@author: cda
'''
import unittest
import logging
import sys
from expense_help import ExpenseHelper
from config import ExpenseConfigParser
from handler.category import EmailCategorizerFactory, CostCenterMatcher
from handler.filter import EmailFilterHandler, EmailCleanup
import re
import shlex
from mail.imap import ImapConnector
from mail.smtp import SmtpConnector
from ConfigParser import ConfigParser
from email.header import Header, make_header
from email.message import Message

class DefaultConfiguration(object):
    def __init__(self):
        self.costcenter_label = 'costcenter'
        self.expense_label = 'expense'
        self.username = 'foo'
        self.imap_server = 'localhost'
        self.smtp_server = 'localhost'
        self.sender = 'me'
        self.receiver = 'me'
        self.subject_pattern = '%(intro)s %(costcenter)s %(payment_type)s %(provider)s %(order_date)s %(outro)s'

class DummyEmail(dict):
    def replace_header(self, header, value):
        self[header] = value
    def add_header(self, header, value):
        self.replace_header(header, value)
    def walk(self):
        return (self,)

def dummy_mail():
    email = DummyEmail()
    email['UID'] = 'foobar1'
    email['DATE'] = '22 Feb 2012 07:09:45 +0800'
    email['FROM'] = 'me@here.de'
    email['Subject'] = 'foobar2',
    email['labels'] = ('costcenter/K11', )
    return email

class DummySmtp(object):
    def close(self):
        pass
    def quit(self):
        pass
    def ehlo(self):
        pass
    def starttls(self):
        pass
    def login(self, username, password):
        pass

class TestPasswordProvider(object):
    def password(self, username):
        return 'foo'
    
class DummyConfigProvider(object):
    def get(self, section, key):
        return 'foo'
    
def dummy_imap_factory(server):
    class DummyImap():
        def login(self, username, password):
            return self
        def list(self):
            return ('OK', ('(\\HasNoChildren) "/" costcenter/K101', '(\\HasNoChildren) "/" spesen/KKJC'))
        def close(self):
            pass
    return ImapConnector(DummyImap())

def dummy_smtp_factory(server):
    return SmtpConnector(DummySmtp())

class ExpenseHelperTest(unittest.TestCase):
    def test_run(self):
        ExpenseHelper(  
                      imap_factory = dummy_imap_factory, 
                      password_provider = lambda x: x, 
                      confirmation_provider = lambda x: 'y', 
                      smtp_factory = dummy_smtp_factory,
                      config_provider = DefaultConfiguration()).run()
    
    def test_categorize_email(self):
        email_categorizer = EmailCategorizerFactory.create(DefaultConfiguration())
        categorized_emails = email_categorizer.categorize('spesen/KKAR', (dummy_mail(), ))
        assert 1 == len(categorized_emails), categorized_emails
        assert 'KKAR' == categorized_emails[0]['categorized']['payment_type'], categorized_emails[0]['categorized']
        assert 'K11' == categorized_emails[0]['categorized']['costcenter'], categorized_emails[0]['categorized']['costcenter']
    
    def test_candidate_filter(self):
        email = dummy_mail()
        email['categorized'] = {'provider' : 'here',
                            'costcenter' : 'K10',
                            'payment_type' : 'KKAR',
                            'order_date' : '02.03.2012'}
        candidates = map(EmailCleanup('from', 'to', DefaultConfiguration().subject_pattern).prepare_outbound, filter(EmailFilterHandler(DummyConfigProvider()).filter_candidate, (email, )))
        for c in candidates:
            self.assertEqual(str(c['Subject']), 
                             '=?iso-8859-1?q?Fwd=3A_K10_KKAR_here_02=2E03=2E2012_=28was=3A_=28=27foobar?=\n =?iso-8859-1?q?2=27=2C=29=29?=')
    def test_parse_labels(self):
        response, label_data = ('OK', ['5 (X-GM-LABELS ("\\\\Sent" "cost center" spesen travel spesen/KKJC) UID 6)'])
        p = re.compile('\d+ \(X-GM-LABELS \((?P<labels>.*)\) UID \d+\)')
        m = p.match(label_data[0])
        assert m, label_data[0]
        assert m.group('labels') == '"\\\\Sent" "cost center" spesen travel spesen/KKJC', m.group('labels')
        assert shlex.split(m.group('labels')) == ['\\Sent', 'cost center', 'spesen', 'travel', 'spesen/KKJC'], shlex.split(m.group('labels'))
    def test_no_cost_center_assigned(self):
        mail = dummy_mail()
        mail['labels'] = 'costcenter'
        self.assertRaisesRegexp(Exception, 'mail has no costcenter \[costcenter\/<costcenter>\] assigned', lambda: CostCenterMatcher(DefaultConfiguration()).costcenter_for(mail))
    def test_config_parser(self):
        e = ExpenseConfigParser(None, None)
        assert hasattr(e, 'username'), e.__dict__
        assert hasattr(e, 'smtp_server'), e.__dict__
        assert hasattr(e, 'imap_server'), e.__dict__
        assert hasattr(e, 'receiver'), e.__dict__
        assert hasattr(e, 'costcenter_label'), e.__dict__
        assert hasattr(e, 'expense_label'), e.__dict__
    def test_store_and_load_config(self):
        from tempfile import NamedTemporaryFile
        f = NamedTemporaryFile(delete = True)
        e = ExpenseConfigParser(ConfigParser(), f.name)
        e.store()
        e.load()
        
    def test_header_conversion(self):
        def convert(string):
            return str(Header(string.encode('iso-8859-1'), 'iso-8859-1'))
        self.assertEqual(convert(unicode('(was: Vielen Dank für Ihren Fahrkartenkauf! (Auftrag TSYLM7))', 'utf-8')), 
                        '=?iso-8859-1?q?=28was=3A_Vielen_Dank_f=FCr_Ihren_Fahrkartenkauf!_=28Auftr?=\n =?iso-8859-1?q?ag_TSYLM7=29=29?=')

    def test_encode_subject(self):
        email = Message()
        email.add_header('Subject', 'Vielen Dank für Ihren Fahrkartenkauf! (Auftrag TSYLM7)')
        email.add_header('From', '_value')
        email['categorized'] = {}
        out_mail = EmailCleanup('_from', 'to', '%(outro)s').prepare_outbound(email)
        self.assertEqual(str(out_mail['Subject']),
                         '=?iso-8859-1?q?=28was=3A_Vielen_Dank_f=FCr_Ihren_Fahrkartenkauf!_=28Auftr?=\n =?iso-8859-1?q?ag_TSYLM7=29=29?=')
        

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.WARN)
    unittest.main()
