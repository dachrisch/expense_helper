'''
Created on Feb 23, 2012

@author: cda
'''
import getpass
import logging
import logging.config
import sys
from mail.imap import connector_for
from email.header import decode_header

def remove_encoding(text):
    texts_with_charsets = decode_header(text)
    decoded_text = ''
    for twc in texts_with_charsets:
        decoded_text += twc[0]
    return decoded_text


def main():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    connection = connector_for('imap.googlemail.com')
    
    username = 'christian.daehn@it-agile.de'
    password = getpass.getpass('password for [%s]: ' % username)
    connection._login(username, password)
    
    expense_inboxes = connection.filter_inboxes(lambda inbox: inbox.startswith('"spesen/'))
    print(expense_inboxes)
    
    for inbox in expense_inboxes:
        emails = connection.read_from(inbox)
        print(map(lambda x: remove_encoding(x['Subject']), emails))

    connection.close()


if __name__ == '__main__':
    main()