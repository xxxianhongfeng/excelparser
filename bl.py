#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: xianhongfeng
@date: 2016-07-26
@description: build lua file
'''

import ep
import re
from ed import BuildError

class LuaGenerator():
	"""
	"""

	def __init__(self, fileName, configDic):
		self.fileName = fileName
		self.configDic = configDic
		self._generateFunc = {ep.TYPE_INT: self.__generate_int_str, ep.TYPE_STRING: self.__generate_str_str, ep.TYPE_ARRAY_INT: self.__generate_array_int_str, ep.TYPE_ARRAY_STRING: self.__generate_array_str_str, ep.TYPE_ARRAY2_INT: self.__generate_array2_int_str, ep.TYPE_ARRAY2_STRING: self.__generate_array2_str_str, ep.TYPE_FLOAT: self.__generate_float_str}

	def build(self):
		content = '''%sConfig = {}\n-- auto generated! don't modify !\n\n%sConfig.Config = {\n''' % ((self.fileName[:self.fileName.find('.')].capitalize(),)*2)
		for config in self.configDic:
			key = '-'.join(unicode(config[i]['value'])[:unicode(config[i]['value']).find('.')] for i in range(len(config)) if config[i]['iskey'])
			content += '%s,\n' % self.__generate_config_str(key, config)
		content += '}\n\nreturn %sConfig' % self.fileName[:self.fileName.find('.')].capitalize()
		return content

	"""
	生成配置表中一行数据的格式化字符串

	"""
	def __generate_config_str(self, key, dic):
		s = '["%s"] = {%s, ' % (key, self.__generate_with_key("key", '"%s"' % key))
		for i in range(len(dic)):
			if dic[i]['outSource'].find('c') >= 0:
				s += '%s, ' % self.__generate_with_key(dic[i]['key'], self.__auto_match_generate(dic[i]))
		return s.rstrip(', ') + '}'

	# dict( (('outSource', outSourceRow[col]), ('type', _DataId[dataTypeRow[col]]), ('key', (keyRow[col])), ('value', sheet.cell(row, col).value), ('iskey', iskeyRow[col].find('key')>=0), ('row', row), ('col', col))
	def __generate_int_str(self, value):
		if not isinstance(value, (int, float)):
			raise TypeError, ('__generate_int_str - value: %s is not int type' % value)
		return '%d' % int(value)

	def __generate_str_str(self, value):
		s = unicode(value)
		if s.endswith('.0'):
			s = s[:-2]
		return '"%s"' % s

	def __generate_array_int_str(self, value):
		if len(re.findall(r'[a-zA-Z]', value.strip('[{}]'))) > 0:
			raise TypeError, ('__generate_array_int_str - value: %s is not array_int type' % value)
		# print "__generate_array_int_str - %s" % value
		# for v in re.compile(r'-?\d+').findall(value):
		# 	print v
		return '{%s}' % ','.join(re.compile(r'-?\d+').findall(value))

	def __generate_array_str_str(self, value):
		if value.strip('[{}]') == "":
			return "{}"
		return '{%s}' % ','.join('"%s"' % s.strip() for s in value.strip('[{}]').split(','))

	def __generate_array2_int_str(self, value):
		if value[:value.find('}')].count('{') >= 2:
			raise TypeError, ('__generate_array2_int_str - dim of array: %s is too deep' % value)
		s = '{'
		for arr in value.split('},'):
			arrStr = self.__generate_array_int_str(arr)
			arrStr = "" if arrStr == "{}" else arrStr
			s = '%s%s, ' % (s, arrStr)
		return s.rstrip(', ') + '}'

	def __generate_array2_str_str(self, value):
		if value[:value.find('}')].count('{') >= 2:
			raise TypeError, ('__generate_array2_str_str - dim of array: %s is too deep' % value)
		s = '{'
		for arr in value.split('},'):
			arrStr = self.__generate_array_str_str(arr)
			arrStr = "" if arrStr == "{}" else arrStr
			s = '%s%s, ' % (s, arrStr)
		return s.rstrip(', ') + '}'

	def __generate_float_str(self, value):
		if not isinstance(value, float):
			raise TypeError, ('__generate_float_str - value: %s is not float type' % value)
		return unicode(value)

	def __generate_with_key(self, key, s):
		return '["%s"]=%s' % (key, s)

	def __auto_match_generate(self, cellInfo):
		try:
			return self._generateFunc[cellInfo['type']](cellInfo['value'])
		except TypeError, e:
			raise BuildError('EXCEL: [%s] \nrow: %d, col: %d : dataType:%s, value:%s   \nerr: %s' % (self.fileName, cellInfo['row']+1, cellInfo['col']+1, ep.TYPE_NAME[cellInfo['type']], unicode(cellInfo['value']), e))