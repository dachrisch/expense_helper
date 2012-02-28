Expense Helper
==============
help to forward emails appropriately labeled in Google Mail to accounting

Gmail organisation
------------------

This program is using Gmail labels to mark emails for delivery and categorization.

First, all mails which can be found in any nested inboxes under <expense>/ are fetched. Next, the email is categorized using:
- the send date, to determine the booking date
- the sender, to determine the booking provider (the domain part of the email is used)
- the nested label under <costcenter>, to determine the cost center
- the nested label under <expense>, to determine the payment type

Example label structure:

	costcenter
	|---------/K10
	           |--- email1 from airberlin.de send 22.2.2012
	          /K100
	           |--- email2 from bahn.de send 23.1.2012
	expense
	|---------/KKJC
	           |--- email1
	          /ELV
	           |--- email2
	           
This will be categorized as [K10 KKJC airberlin 22.02.2012] and [K100 ELV bahn 23.01.2012]

program usage
-------------
	Usage: expense_help.py [options]
	
	Options:
	  -h, --help            show this help message and exit
	  -i FILE, --ini-file=FILE
	                        read configuration from FILE (default: expense.ini)
	  -v, --verbose         print status messages to stdout more verbose
	  -c, --create-default-config
	                        create a default config file
	  -y, --yes             don't ask questions
	                        
configuration
-------------

example:
	
	[mail]
	username=<username>
	imap_server=imap.googlemail.com
	smtp_server=smtp.googlemail.com
	[account]
	destination=<receipient>
	[labels]
	costcenter=costcenter/
	expense=spesen/
	delivered=delivered


requirements
------------
None.

continuous integration
----------------------
[![Build Status](https://secure.travis-ci.org/dachrisch/expense_helper.png?branch=master)](http://travis-ci.org/dachrisch/expense_helper)

CI provided by http://travis-ci.org/
