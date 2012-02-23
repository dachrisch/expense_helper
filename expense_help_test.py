'''
Created on Feb 23, 2012

@author: cda
'''
import unittest
import logging
import sys
from expense_help import ExpenseHelper
from category import EmailCategorizerFactory, EmailFilter

class DummyEmail(dict):
    def replace_header(self, header, value):
        self[header] = value

def dummy_mail():
    email = DummyEmail()
    email['Message-ID'] = 'foobar1'
    email['DATE'] = '22 Feb 2012 07:09:45 +0800'
    email['FROM'] = 'me@here.de'
    email['Subject'] = 'foobar2',
    email['categorized'] = {'provider' : 'here',
                            'costcenter' : 'K10',
                            'payment_type' : 'KKAR',
                            'order_date' : '02.03.2012'}
    return email

class DummyImapConnector(object):
    def _login(self, username, password):
        return self
    def filter_inboxes(self, criteria):
        if criteria('"costcenter/'):
            return ('costcenter/K10', 'costcenter/K500')
        elif criteria('"spesen/'):
            return ('spesen/KKAR', )
    def read_from(self, inbox, query):
        return (dummy_mail(), )
    def close(self):
        pass

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

def test_imap_factory(server):
    return DummyImapConnector()

def test_smtp_factory(server):
    return DummySmtpConnector()

class ExpenseHelperTest(unittest.TestCase):
    def xtest_run(self):
        ExpenseHelper(imap_factory = test_imap_factory, password_provider = lambda x: x, confirmation_provider = lambda x: 'y', smtp_factory = test_smtp_factory).run()
    
    def xtest_categorize_email(self):
        email_categorizer = EmailCategorizerFactory.create(DummyImapConnector())
        categorized_emails = email_categorizer.categorize('spesen/KKAR', (dummy_mail(), ))
        assert 1 == len(categorized_emails), categorized_emails
        assert 'KKAR' == categorized_emails[0]['categorized']['payment_type'], categorized_emails[0]['categorized']
    
    def test_candidate_filter(self):
        candidates = EmailFilter().filter_candidates((dummy_mail(), ))
        for c in candidates:
            assert 'Fwd: K10 KKAR here 02.03.2012 (was: foobar2)' == c['Subject'], c['Subject']
        
if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()
