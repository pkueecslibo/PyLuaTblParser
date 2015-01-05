#!/usr/bin/env python

def testPyLuaTblParser():
	import PyLuaTblParser as P
	# test load and dump
	a = P.PyLuaTblParser()
	b = P.PyLuaTblParser()
	test_str = '{array = {65,23,5,},dict = {mixed = {43,54.33,false,9,string = "value",},array = {3,6,4,},string = "value",},}'
	a.load(test_str)
	test_str1 = a.dump()
	b.load(test_str1)
	test_str2 = b.dump()
	assert(a.data == b.data)
	assert(test_str1 == test_str2)
	test_str = '{x=-0xffp-2, y=45;--[===[adsfasdf]==]asdfasfd]===]"a", "one", "two", "three",[2]=3}'
	a.load(test_str)
	assert(a.data != b.data)
	test_str1 = a.dump()
	b.load(test_str1)
	test_str2 = b.dump()
	assert(a.data == b.data)
	assert(test_str1 == test_str2)
	# test loadLuaTable and dumpLuaTable
	a.loadLuaTable("test.txt")
	a.dumpLuaTable("test2.txt")
	b.loadLuaTable("test2.txt")
	assert(a.data == b.data)
	# test loadDict and dumpDict
	d = {1: 'a', 2: 'one', 3: 'two', 4: 'three', 'y': 45, 'x': -63.75}
	a.loadDict(d)
	assert(a.data == d)
	di = a.dumpDict()
	assert(d == di)
	d = {'array': [65, 23, 5], 'dict': {'mixed': {1: 43, 2: 54.33, 3: False, 4: 9, 'string': 'value'}, 'array': [3, 6, 4], 'string': 'value'}}
	assert(d != di)
	assert(d != a.data)
	a.loadDict(d)
	assert(a.data == d)
	assert(a.data != di)
	di = a.dumpDict()
	assert(a.data == di)

if __name__ == "__main__":
	testPyLuaTblParser()
	


