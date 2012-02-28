Expense Helper
==============
help to forward emails appropriately labeled in Google Mail to accounting

usage
-----

	Usage: expense_help.py [options]
	
	Options:
	  -h, --help            show this help message and exit
	  -i FILE, --ini-file=FILE
	                        read configuration from FILE (default: expense.ini)
	  -v, --verbose         print status messages to stdout more verbose
	  -c, --create-default-config
	                        create a default config file
	                        
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


requirements
------------
None.

continuous integration
----------------------
[![Build Status](https://secure.travis-ci.org/dachrisch/expense_helper.png?branch=master)](http://travis-ci.org/dachrisch/expense_helper)

CI provided by http://travis-ci.org/
