#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: xianhongfeng
@date: 2016-07-26
@description: entrance of excel to lua,c#,erlang

'''

import ep
import bl
import be
import bc
import os
import sys
import re
import time
import xlrd
# import threading
from ed import BuildError

def build_lua(_type, fn, cdic, oPath):
	try:
		if _type.find('lua') == -1:
			return
		content = bl.LuaGenerator(fn, cdic).build()
	except BuildError, e:
		print 'build_lua ERROR --[[\n', unicode(e), ']]--'
	else:
		f = open('%s/%sConfig.lua.txt' % (oPath, fn[:fn.find('.')].capitalize()), 'w')
		f.write(content.encode('utf-8'))
		f.close()

def build_erlang(_type, fn, cdic, oPath):
	try:
		if _type.find('erlang') == -1:
			return
		content = be.ErlangGenerator(fn, cdic).build()
	except BuildError, e:
		print 'build_erlang ERROR --[[\n', unicode(e), ']]--'
	else:
		f = open('%s/%s_dat.erl' % (oPath, fn[:fn.find('.')].lower()), 'w')
		f.write(content.encode('utf-8'))
		f.close()

def build_cs(_type, fn, cdic, oPath):
	try:
		if _type.find('c#') == -1:
			return
		byte = bc.CSGenerator(fn, cdic).build()
		vo = bc.CSVoGenerator(fn, cdic).build()
	except BuildError, e:
		print 'build_c# ERROR --[[\n', unicode(e), ']]--'
	else:
		f = open('%s/%sVo.bytes' % (oPath, fn[:fn.find('.')].capitalize()), 'wb')
		f.write(byte)
		f.close()

		f = open('%s/%sVo.cs' % (oPath, fn[:fn.find('.')].capitalize()), 'w')
		f.write(vo.encode('utf-8'))
		f.close()

def build_errcode_file(oPath):
	try:
		book = xlrd.open_workbook("%s/error_code.xlsx" % sys.argv[2])
		sheet = book.sheet_by_index(0)
	except Exception, e:
		print 'build_errcode_file ERROR error_code.xlsx is not exist', e
	else:
		context = '%%%----------------------------------------------------------------------\n'
		context += '%%%\n'
		context += '%%% @author: liuweidong\n'
		context += '%%% @doc: game errcode define\n'
		context += '%%%       auto generate, do not modify\n'
		context += '%%% @end\n'
		context += '%%%----------------------------------------------------------------------\n\n'
		for i in range(6, sheet.nrows):
			row_data = sheet.row_values(i)
			context += '-define(%-30s        %s).    %%%% %s\n' % (row_data[1]+',', int(row_data[0]), row_data[3])

		f = open("%s/errcode.hrl" % oPath, 'w')
		f.write(context.encode('utf-8'))
		f.close()

def build_define_file(oPath):
	try:
		book = xlrd.open_workbook('%s/define.xlsx' % sys.argv[2])
		sheet = book.sheet_by_index(0)
	except Exception, e:
		print 'build_define_file ERROR define.xlsx is not exist', e
	else:
		context = '%%%----------------------------------------------------------------------\n'
		context += '%%%\n'
		context += '%%% @author: liuweidong\n'
		context += '%%% @doc: game errcode define\n'
		context += '%%%       auto generate, do not modify\n'
		context += '%%% @end\n'
		context += '%%%----------------------------------------------------------------------\n\n'
		for i in range(1, sheet.nrows):
			row_data = sheet.row_values(i)
			context += '-define(%-30s        %s).    %%%% %s\n' % (row_data[0]+',', int(row_data[1]), row_data[2])

		f = open("%s/define.hrl" % oPath, 'w')
		f.write(context.encode('utf-8'))
		f.close()

def remove_file(_dir, extList):
	if os.path.isdir(_dir):
		for f in os.listdir(_dir):
			remove_file('%s/%s' % (_dir, f), extList)
	else:
		for e in extList:
			if os.path.splitext(_dir)[1] == e:
				os.remove(_dir)

def do_build(fp, fn, oType, oPath):
	_ep = ep.ExcelParser(fp)
	_type, cdic = _ep.parse()
	f[oType](_type, fn, cdic, oPath)

if __name__ == '__main__' and len(sys.argv) > 3:
	stime = time.time()
	oType = sys.argv[1]
	ePath = sys.argv[2]
	oPath = sys.argv[3]
	single = False
	if len(sys.argv) > 4:
		target = sys.argv[4]
		single = True

	"""
	获取指定路径中所有xlsx,xls,xlsm文件的路径

	"""
	eplist = []
	for root, dirs, files in os.walk(ePath):
		for fp in (os.path.join(root, f) for f in files if os.path.splitext(f)[1] in ('.xlsx','.xls','.xlsm')):
			if (not single) or (single and fp[fp.find('\\')+1:fp.find('.')] == target):
				eplist.append(fp)
	print eplist

	try:
		f = {'lua': build_lua, 'cs': build_cs, 'erlang': build_erlang}
		postfix = {'lua': ('.txt'), 'cs': ('.bytes', '.cs'), 'erlang': ('.erl')}
		if not single:
			remove_file(oPath, postfix[oType])
			if oType == 'erlang':
				build_errcode_file(oPath)
		        build_define_file(oPath)

		# threads = []
		for fp in eplist:
			fp = fp.replace('\\', '/')
			fn = fp[fp.rfind('/')+1:]
			if re.match(r'\w+[^a-z_]', os.path.splitext(fn)[0]):
				continue
			do_build(fp, fn, oType, oPath)
			# t = threading.Thread(target = do_build, args = (fp, fn, oType, oPath))
			# threads.append(t)

		# for t in threads:
		# 	t.start()
		# for t in threads:
		# 	t.join()
		print 'build %s ok  time: %f' % (oType, time.time() - stime)
	except BuildError, e:
		print 'excel parse ERROR --[[\n', unicode(e), ']]--'
	except KeyError, e:
		print 'KeyError: %s is not in ["lua", "cs", "erlang"]' % oType