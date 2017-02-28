#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: xianhongfeng
@date: 2016-07-25
@description: excel parser
'''

import xlrd
import os
import sys

from ed import BuildError

TYPE_INT = 1
TYPE_STRING = 2
TYPE_ARRAY_INT = 3
TYPE_ARRAY_STRING = 4
TYPE_ARRAY2_INT = 5
TYPE_ARRAY2_STRING = 6
TYPE_FLOAT = 7

TYPE_NAME = { TYPE_INT: 'int', TYPE_STRING: 'string', TYPE_ARRAY_INT: 'array_int', TYPE_ARRAY_STRING: 'array_str', TYPE_ARRAY2_INT: 'array2_int', TYPE_ARRAY2_STRING: 'array2_str', TYPE_FLOAT: 'float' }

_DataId = { "int": TYPE_INT, "string": TYPE_STRING, "array_int": TYPE_ARRAY_INT, "array_str": TYPE_ARRAY_STRING, "array2_int": TYPE_ARRAY2_INT, "array2_str": TYPE_ARRAY2_STRING, "float": TYPE_FLOAT }

class ExcelParser(object):
    """
    """
    def __init__(self, excelPath):
        if not isinstance(excelPath, str):
            raise TypeError, 'excelPath must be type of string' 
        self.excelPath = excelPath
        t = excelPath.rfind('/')
        t = 0 if t < 0 else t+1
        self.fileName = excelPath[t:excelPath.rfind('.')]

    def parse(self):
        book = xlrd.open_workbook(self.excelPath)
        sheet = book.sheet_by_index(0)
        typeInfo = sheet.row_values(0)[0]
        # if typeInfo.find('lua') == -1:
        #     return

        ncols = sheet.ncols
        nrows = sheet.nrows
        try:
            keyRow = [sheet.row_values(2)[i] for i in range(ncols)]
        except IndexError, e:
            print 'EXCEL: [%s] row for key is missing' % self.fileName
            return typeInfo, list()
        else:
            dataTypeRow = [sheet.row_values(3)[i].lower() for i in range(ncols)]
            outSourceRow = [sheet.row_values(4)[i] for i in range(ncols)]
            iskeyRow = [sheet.row_values(5)[i] for i in range(ncols)]

            configs = []
            for row in range(6, nrows):
                try:
                    config = [( col, dict( (('outSource', outSourceRow[col]), ('type', _DataId[dataTypeRow[col]]), ('key', (keyRow[col])), ('value', sheet.cell(row, col).value), ('iskey', iskeyRow[col].find('key')>=0), ('row', row), ('col', col)) ) ) for col in range(ncols)]
                except KeyError ,e:
                    raise BuildError('EXCEL: [%s] \nrow: %d col: %d : dataType: [%s] is not exist \nerr: dataType should be one of ("int", "string", "array_int", "array_str", "array2_int", "array2_str", "float")' % (self.fileName, row+1, col+1, dataTypeRow[col]))
                except AttributeError, e:
                    raise BuildError('EXCEL: [%s] \nrow: %d col: %d :  \nerr: keyFlag: ["%s"] is must be type of string' % (self.fileName, row+1, col+1, iskeyRow[col]))
                else:
                    configs.append(dict(config))

            return typeInfo ,list(configs)


if __name__ == "__main__" and len(sys.argv) > 1:
    path = os.getcwd()
    filePath = sys.argv[1]
    _ep = ExcelParser(filePath)
    for config in _ep.parse()[1]:
        print config
