'''
Created on Feb 23, 2012

@author: cda
'''
import imaplib
import getpass

def main():
    print('connect to server...')
    imap = imaplib.IMAP4_SSL('imap.googlemail.com', 993)
    
    username = 'christian.daehn@it-agile.de'
    password = getpass.getpass('password for [%s]: ' % username)
    imap.login(username, password)
    
    print('fetching expense inboxes...')
    status, available_inboxes = imap.list()
    assert status == 'OK', status
    expense_inboxes = filter(lambda inbox: inbox.startswith('(\\HasNoChildren) "/" "spesen/'), available_inboxes)
    print(expense_inboxes)
    imap.select('spesen')
    response, serach_data = imap.search(None, 'ALL')
    ids = serach_data[0].split()

    response, raw_uids = imap.uid('FETCH', '1:*', '(UID)')
    
    print(raw_uids)

    imap.close()


if __name__ == '__main__':
    main()