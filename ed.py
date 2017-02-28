#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: xianhongfeng
@date: 2016-07-27
@description: error define
'''

class BuildError(Exception): 
    def __init__(self, text):
        Exception.__init__(self)
        self.text = text
    def __str__(self):
        return self.text		