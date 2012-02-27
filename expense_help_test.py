'''
Created on Feb 23, 2012

@author: cda
'''
import unittest
import logging
import sys
from expense_help import ExpenseHelper
from category import EmailCategorizerFactory, EmailFilter
import ConfigParser
import re
import shlex
from mail.imap import ImapConnector

class DefaultConfiguration(object):
    def get(self, section, property):
        if 'labels' == section:
            if property == 'costcenter':
                return 'costcenter/'
            if property == 'expense':
                return 'sepsen/'
    def read(self, file):
        assert file == 'expense.ini'

class DummyEmail(dict):
    def replace_header(self, header, value):
        self[header] = value
    def add_header(self, header, value):
        self.replace_header(header, value)

def dummy_mail():
    email = DummyEmail()
    email['UID'] = 'foobar1'
    email['DATE'] = '22 Feb 2012 07:09:45 +0800'
    email['FROM'] = 'me@here.de'
    email['Subject'] = 'foobar2',
    email['labels'] = ('costcenter/K11', )
    return email

class DummySmtpConnector(object):
    def _login(self, username, password):
        return self
    def email(self, email):
        pass    
    def logout(self):
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
    return DummySmtpConnector()

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
        candidates = EmailFilter(DummyConfigProvider()).filter_candidates((email, ))
        for c in candidates:
            assert 'Fwd: K10 KKAR here 02.03.2012 (was: foobar2)' == c['Subject'], c['Subject']
    def test_parse_labels(self):
        response, label_data = ('OK', ['5 (X-GM-LABELS ("\\\\Sent" "cost center" spesen travel spesen/KKJC) UID 6)'])
        p = re.compile('\d+ \(X-GM-LABELS \((?P<labels>.*)\) UID \d+\)')
        m = p.match(label_data[0])
        assert m, label_data[0]
        assert m.group('labels') == '"\\\\Sent" "cost center" spesen travel spesen/KKJC', m.group('labels')
        assert shlex.split(m.group('labels')) == ['\\Sent', 'cost center', 'spesen', 'travel', 'spesen/KKJC'], shlex.split(m.group('labels'))

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.WARN)
    unittest.main()
