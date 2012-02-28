#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Feb 28, 2012

@author: cda
'''
import logging
class ExpenseConfigParser(object):
    property_mapping = {
                        'username' : ('mail', 'username'),
                        'imap_server' : ('mail', 'imap_server'),
                        'smtp_server' : ('mail', 'smtp_server'),
                        'receiver' : ('account', 'destination'),
                        'costcenter_label' : ('labels', 'costcenter'),
                        'expense_label' : ('labels', 'expense'),
                        }
    def __init__(self, config_parser, filename):
        self.config_parser = config_parser
        self.filename = filename
        self.log = logging.getLogger('ExpenseConfigParser')
        map(self.__property_set(lambda option: None), ExpenseConfigParser.property_mapping.keys())
            
    def load(self):
        if not self.config_parser:
            raise Exception('no config parser set')
        self.log.info('reading configuration from [%s]' % self.filename)
        self.config_parser.read(self.filename)
        map(self.__property_set(lambda option: self.__checked_get(ExpenseConfigParser.property_mapping[option][0], ExpenseConfigParser.property_mapping[option][1])), 
            ExpenseConfigParser.property_mapping.keys())
        return self
    def store(self):
        self.log.info('creating default configuration [%s]...' % self.filename)
        map(self.__property_set(lambda option: self.__checked_set(ExpenseConfigParser.property_mapping[option][0], 
                                                                ExpenseConfigParser.property_mapping[option][1],
                                                                '<%s:%s>' % ExpenseConfigParser.property_mapping[option])), 
            ExpenseConfigParser.property_mapping.keys())
        with open(self.filename, 'w') as f:
            self.config_parser.write(f)

    def __property_set(self, value_provider):
        return lambda option: setattr(self, option, value_provider(option))
    def __checked_get(self, section, option):
        if not self.config_parser.has_section(section):
            raise Exception('no such section [%s] in [%s]' % (section, self.filename))
        if not self.config_parser.has_option(section, option):
            raise Exception('no such option [%s] in section [%s] in [%s]' % (section, option, self.filename))

        return self.config_parser.get(section, option)
    def __checked_set(self, section, option, value):
        if not self.config_parser.has_section(section):
            self.config_parser.add_section(section)

        return self.config_parser.set(section, option, value)
