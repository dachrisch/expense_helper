'''
Created on Feb 23, 2012

@author: cda
'''
import unittest
import logging
import sys
import time
from expense_help import ExpenseHelper
class ExpenseHelperTest(unittest.TestCase):
    def test_run(self):
        class DummyEmail(dict):
            def replace_header(self, header, value):
                pass
        class DummyImapConnector(object):
            def _login(self, username, password):
                return self
            def filter_inboxes(self, criteria):
                return ('costcenter/K10', 'costcenter/K500')
            def read_from(self, inbox, query):
                email = DummyEmail()
                email['Message-ID'] = 'foobar'
                email['DATE'] = '22 Feb 2012 07:09:45 +0800'
                email['FROM'] = 'me@here.de'
                email['Subject'] = 'foobar'
                return (email, )
            def close(self):
                pass
        class DummySmtpConnector(object):
            def _login(self, username, password):
                return self
            def email(self, email):
                pass    
            def logout(self):
                pass
        def test_imap_factory(server):
            return DummyImapConnector()
        def test_smtp_factory(server):
            return DummySmtpConnector()
        class TestPasswordProvider(object):
            def password(self, username):
                return 'foo'
        ExpenseHelper(imap_factory = test_imap_factory, password_provider = lambda x: x, confirmation_provider = lambda x: 'y', smtp_factory = test_smtp_factory).run()
        
if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    unittest.main()
