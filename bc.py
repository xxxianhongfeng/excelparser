#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: xianhongfeng
@date: 2016-09-21
@description: build c# file
'''

import ep
import re
import struct

from ed import BuildError

_TYPE_MAP = { ep.TYPE_INT: 'int', ep.TYPE_STRING: 'string', ep.TYPE_ARRAY_INT: 'List<int>', ep.TYPE_ARRAY_STRING: 'List<string>', ep.TYPE_ARRAY2_INT: 'List<List<int>>', ep.TYPE_ARRAY2_STRING: 'List<List<string>>', ep.TYPE_FLOAT: 'float' }

class CSVoGenerator():
	"""
	"""
	def __init__(self, fileName, configDic):
		self.fileName = fileName
		self.configDic = configDic

	def build(self):
		content = '''//auto generate dont modify\nusing System;\nusing System.Collections.Generic;\nusing System.Linq;\nusing System.Text;\n[System.Serializable]\npublic class %sVo\n{''' % self.fileName[:self.fileName.find('.')].capitalize()
		if len(self.configDic) > 0:
			content += self.__generate_vo_define(self.configDic[0])
		content += '''\n\tpublic string GetKey()\n\t{\n\t\treturn key;\n\t}\n}'''
		return content

	def __generate_vo_define(self, dic):
		s = "\n\tpublic string key;"
		for i in range(len(dic)):
			if dic[i]['outSource'].find('c') >= 0:
				s += '\n\tpublic %s %s;' % (_TYPE_MAP[dic[i]['type']], dic[i]['key'])
		return s

##  二进制数打包格式
##[字段个数][字段类型+字段名长度+字段名]....[键值长度+键值+配置数据]... 
##配置数据 = [数据类型 + 数据信息]
#          = array  => 维度+数据类型+数据
#                        数据类型 = string， 数据 = 数据个数+[数据长度+数据]
#                        数据类型 = int，    数据 = 数据个数+[数据]
#                        数据类型 = float，  数据 = 数据个数+[数据]
#           string => [数据长度+数据]
#           int    => [数据]
#           float  => [数据]
class CSGenerator():
	"""
	"""
	def __init__(self, fileName, configDic):
		self.fileName = fileName
		self.configDic = configDic
		self._generateFunc = {ep.TYPE_INT: self.__generate_int_str, ep.TYPE_STRING: self.__generate_str_str, ep.TYPE_ARRAY_INT: self.__generate_array_int_str, ep.TYPE_ARRAY_STRING: self.__generate_array_str_str, ep.TYPE_ARRAY2_INT: self.__generate_array2_int_str, ep.TYPE_ARRAY2_STRING: self.__generate_array2_str_str, ep.TYPE_FLOAT: self.__generate_float_str}

	def build(self):
		byte = self.__generate_config_base_info()
		for config in self.configDic:
			key = '-'.join(str(config[i]['value'])[:str(config[i]['value']).find('.')] for i in range(len(config)) if config[i]['iskey']).encode('utf-8')
			byte += struct.pack('i%is' % len(key), len(key), key)
			byte += self.__generate_config_str(key, config)
		return byte

	# dict( (('outSource', outSourceRow[col]), ('type', _DataId[dataTypeRow[col]]), ('key', (keyRow[col])), ('value', sheet.cell(row, col).value), ('iskey', iskeyRow[col].find('key')>=0), ('row', row), ('col', col))
	def __generate_config_base_info(self):
		byte = ''
		if len(self.configDic) > 0:
			num = 0
			for i in range(len(self.configDic[0])):
				if self.configDic[0][i]['outSource'].find('c') >= 0:
					num += 1
					dic = self.configDic[0][i]
					key = dic['key'].encode('utf-8')
					byte += struct.pack('ii%is' % len(key), dic['type'], len(key), key)
			byte = struct.pack('i', num) + byte
		return byte


	"""
	生成配置表中一行数据的格式化字符串
	"""
	def __generate_config_str(self, key, dic):
		b = ''
		for i in range(len(dic)):
			if dic[i]['outSource'].find('c') >= 0:
				# if key == '101': print i, dic[i]['value']
				b += self.__auto_match_generate(dic[i])
		return b

	# dict( (('outSource', outSourceRow[col]), ('type', _DataId[dataTypeRow[col]]), ('key', (keyRow[col])), ('value', sheet.cell(row, col).value), ('iskey', iskeyRow[col].find('key')>=0), ('row', row), ('col', col))
	def __generate_int_str(self, value):
		if not isinstance(value, (int, float)):
			raise TypeError, ('__generate_int_str - value: %s is not int type' % value)
		return struct.pack('i', int(value))

	def __generate_str_str(self, value):
		s = unicode(value)
		if s.endswith('.0'):
			s = s[:-2]
		s = s.encode('utf-8')
		return struct.pack('i%is' % len(s), len(s), s)

	def __generate_array_int_str(self, value):
		if len(re.findall(r'[a-zA-Z]', value.strip('[{}]'))) > 0:
			raise TypeError, ('__generate_array_int_str - value: %s is not array_int type' % value)
		l = re.compile(r'\d+').findall(value)
		num = len(l)
		b = struct.pack('i', num)
		for i in range(num):
			b += struct.pack('i', int(l[i]))
		return b

	def __generate_array_str_str(self, value):
		if value.strip('[{}]') == "":
			return struct.pack('i', 0)
		l = value.strip('[{}]').split(',')
		num = len(l)
		b = struct.pack('i', num)
		for i in range(num):
			s = l[i].strip().encode('utf-8')
			b += struct.pack('i%is' % len(s), len(s), s)
		return b

	def __generate_array2_int_str(self, value):
		if value[:value.find('}')].count('{') >= 2:
			raise TypeError, ('__generate_array2_int_str - dim of array: %s is too deep' % value)
		l = value.split('},')
		num = len(l)
		bb = struct.pack('i', num)
		for arr in l:
			b = self.__generate_array_int_str(arr)
			bb += b
		return bb

	def __generate_array2_str_str(self, value):
		if value[:value.find('}')].count('{') >= 2:
			raise TypeError, ('__generate_array2_str_str - dim of array: %s is too deep' % value)
		l = value.split('},')
		num = len(l)
		bb = struct.pack('i', num)
		for arr in l:
			b = self.__generate_array_str_str(arr)
			bb += b
		return bb

	def __generate_float_str(self, value):
		if not isinstance(value, float):
			raise TypeError, ('__generate_float_str - value: %s is not float type' % value)
		return struct.pack('f', float(value))

	def __generate_with_key(self, key, s):
		pass

	def __auto_match_generate(self, cellInfo):
		try:
			return self._generateFunc[cellInfo['type']](cellInfo['value'])
		except TypeError, e:
			raise BuildError('EXCEL: [%s] \nrow: %i, col: %i : dataType:%s, value:%s   \nerr: %s' % (self.fileName, cellInfo['row']+1, cellInfo['col']+1, ep.TYPE_NAME[cellInfo['type']], unicode(cellInfo['value']), e))
