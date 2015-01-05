#!/usr/bin/env python
import math
class LuaError(Exception):

	def __str__(self):
		return repr("illegal lua string")
	
class PyError(Exception):

	def __str__(self):
		return repr("illegal python type")

class FpError(Exception):

	def __str__(self):
		return repr("python file io exception")

class PyLuaTblParser():

	def __init__(self):
		self.data = {}
		self.strlen = None
	
	def load(self, s):	
		self.strlen = len(s)
		self.data, beg = self.parseTable(s, 0)
		beg = self.escape(s, beg)
		if beg < self.strlen: raise LuaError()

	def equals(self, s, beg, end, t):
		# judge if s[beg:end] == t 
		strlen = self.strlen
		if end > strlen: return False
		return s[beg:end] == t

	def escapeWhitespace(self, s, beg):
		strlen = self.strlen
		while (beg < strlen) and s[beg].isspace():
			beg += 1
		return beg
	
	def escapeComment(self, s, beg):	
		strlen = self.strlen
		if self.equals(s, beg, beg + 3, "--["):
			# lua block comment ?
			end = beg + 3
			while self.equals(s, end, end + 1, "="):
				end += 1
			# lua blocak comment
			if self.equals(s, end, end + 1, "["):
				# ]=== ...]
				right = "]" + s[beg+3:end] + "]"
				length = end-beg-1
				end += 1
				while (end+length <= strlen) and \
				(s[end:end+length] != right):
					end += 1
				if end + length > strlen:	
					raise LuaError()
				else:
					return end + length
			# lua line comment
			else:
				while (end < strlen) and (s[end] != '\n'):
					end += 1
				return end + 1
		else:
			# line comment
			end = beg + 2
			while (end < strlen) and (s[end] != '\n'):
				end += 1
			return end + 1

	def check(self, beg):
		if beg >= self.strlen: raise LuaError()
		return True
	
	# escape whitespace and lua comment
	def escape(self, s, beg):
		while beg < self.strlen:
			beg = self.escapeWhitespace(s, beg)
			if self.equals(s, beg, beg+2, "--"):
				beg = self.escapeComment(s, beg)
			else:
				break
		return beg

	def store(self, di, maxn, isList):
		if isList:
			li = []
			for i in range(1, maxn):
				li.append(di[i])
			return li
		else:
			dt = {}
			for k, v in di.iteritems():
				if v != None:
					dt[k] = v
			return dt

	def isShortcut(self, char):
		return (char == '_' or char.isdigit() \
		or char.isalpha())
	
	def isNumber(self, number):
		return (isinstance(number, int) or \
		isinstance(number, long) or \
		isinstance(number, float))
	
	def isString(self, string):
		return (isinstance(string, str) or \
		isinstance(string, unicode))

	def checkConstant(self, key):
		if key == "nil": return True, None
		if key == "true": return True, True
		if key == "false": return True, False
		return False, None

	# need to handle ,; more
	def parseTable(self, s, beg):
		# escape whitespace and lua comment
		beg = self.escape(s, beg)
		self.check(beg)
		# check {
		if s[beg] != '{': raise LuaError()
		beg += 1
		di = {}
		maxn = 1
		isList = True
		# check if have {[k]=v [k]=v}
		twoKV = False
		# check if have {,;}
		twoDt = True
		# check if is {}
		empty = True
		while True:
			# escape whitespace and lua comment
			beg = self.escape(s, beg)
			self.check(beg)
			# parse a table
			if s[beg] == '}':
				if empty: return {}, beg+1
				return self.store(di, maxn, isList), beg+1
			# is delimileter
			elif s[beg] == ',' or s[beg] == ';':
				if twoDt: raise LuaError()
				else: 
					twoDt = True
					twoKV = False
					beg += 1
			else:
				if twoKV: raise LuaError()
				twoKV = True
				twoDt = False	
				# is a new table
				if s[beg] == '{':
					value, beg = self.parseTable(s, beg)
					di[maxn] = value
					maxn += 1
				# is lua string
				elif self.equals(s, beg, beg+2, "[["):
					value, beg = self.parseString(s, beg)
					di[maxn] = value
					maxn += 1
				# is a ([key] = value) pair
				elif s[beg] == '[':
					# parse key
					isList = False
					beg += 1
					key, beg = self.parseValue(s, beg)
					beg = self.escape(s, beg)
					self.check(beg)
					if s[beg] != ']': raise LuaError()
					# parse value
					beg += 1
					beg = self.escape(s, beg)
					self.check(beg)
					if s[beg] != '=': raise LuaError()
					beg += 1
					value, beg = self.parseValue(s, beg)
					# already have a privalage number key
					if self.isNumber(key) and (key in di): continue
					di[key] = value
				# is lua shortcut
				elif s[beg] == '_' or s[beg].isalpha():
					key, beg = self.parseShortcut(s, beg)	
					yes, value = self.checkConstant(key)
					# is constant
					if yes: 
						di[maxn] = value
						maxn += 1
					# is a key
					else:
						isList = False
						beg = self.escape(s, beg)
						self.check(beg)
						# is a (key, value) pair
						if s[beg] == '=':
							beg += 1
							value, beg = self.parseValue(s, beg)
							di[key] = value
				# is lua string or number
				elif s[beg] == '"' or s[beg] == "'" or \
				("-0123456789.".find(s[beg]) > -1):
					value, beg = self.parseString(s, beg)
					di[maxn] = value
					maxn += 1
				# illegal character
				else:
					raise LuaError()
			empty = False
	
	def parseNumber(self, s, beg):	
		sign = 1
		end = beg
		if s[end] == "-":
			sign = -1
			end += 1
		# base 16
		if self.equals(s, end, end+2, "0x") or \
		self.equals(s, end, end+2, "0X"):
			end += 2
			beg = end
			dot = None
			number = False
			while (end < self.strlen):
				if s[end] == '.':
					if dot: raise LuaError()
					dot = end
				elif ("0123456789abcedf".find(s[end].lower()) > -1):
					end += 1
					number = True
				else:
					break
			if not number: raise LuaError()
			if not dot: dot = end
			# number before dot
			a = 0
			for i in range(beg, dot):
				a = a * 16 + int(s[i], 16)
			# number after dot
			b = 0
			for i in reversed(range(dot+1, end)):
				b = (b + int(s[i], 16)) / 16.0
			number = sign * (a + b)
			self.check(end)
			# ends with p123...
			if s[end].lower() == "p":
				end += 1
				beg = end
				self.check(end)
				while (end < self.strlen) and \
				("+-0123456789".find(s[end]) > -1):
					end += 1
				try:
					p = int(s[beg:end])
					number *= math.pow(2, p)
					return number, end
				except:
					raise LuaError()
			else:
				return number, end
		# base 10
		else:
			while (end < self.strlen) and \
			("+-0123456789.e".find(s[end].lower()) > -1):
				end += 1
			try:
				number = eval(s[beg:end])
				return number, end
			except:
				raise LuaError()

	def dealString(self, s, beg, endChar):
		escapeList = {
			'\\"': '\"',
			"\\'": "\'", 
			"\\b": "\b", 
			"\\f": "\f", 
			"\\r": "\r", 
			"\\n": "\n",
			"\\t": "\t",
			"\\u": "u",
			"\\\\":"\\",
			"\\/": "/", 
			"\\a": "\a",
			"\\v": "\v"
		}
		if self.equals(s, beg, beg+2, "[["):
			beg += 2
		else:
			beg += 1
		li = []
		if endChar == "]]":
			while True:
				self.check(beg)
				if self.equals(s, beg, beg+2, endChar):
					return "".join(li), beg + 2
				elif s[beg] == "\\":
					found = False
					for k in escapeList:
						if self.equals(s, beg, beg+2, k):
							li.append(escapeList[s[beg+1]])
							beg += 2
							found = True
							break
					if not found: raise LuaError()
				else:
					li.append(s[beg])
					beg += 1
		else:
			while True:
				self.check(beg)
				if s[beg] == endChar:
					return "".join(li), beg + 1
				elif s[beg] == "\\":
					found = False
					for k in escapeList:
						if self.equals(s, beg, beg+2, k):
							li.append(escapeList[k])
							beg += 2
							found = True
							break
					if not found: raise LuaError()
				else:
					li.append(s[beg])
					beg += 1
			
	def parseString(self, s, beg):
		li = []
		isStr = False
		while True:
			if ("-0123456789.".find(s[beg]) > -1):
				number, beg = self.parseNumber(s, beg)
				li.append(str(number))
			else:
				isStr = True
				substr = None
				if s[beg] == '"':
					substr, beg = self.dealString(s, beg, '"')
				elif s[beg] == "'":
					substr, beg = self.dealString(s, beg, "'")
				elif self.equals(s, beg, beg+2, "[["):
					substr, beg = self.dealString(s, beg, "]]")
				else:
					raise LuaError()
				li.append(substr)
			beg = self.escape(s, beg)
			self.check(beg)
			# may be need concat
			if self.equals(s, beg, beg+2, ".."):
				beg += 2
				self.check(beg)
				# more dot ?
				if s[beg] == ".": raise LuaError()
				isStr = True
				self.escape(beg)
				self.check(beg)
			else:
				break
		if isStr: return "".join(li), beg
		else: return eval(li[-1]), beg
			
	def parseConstant(self, s, beg):
		end = beg
		while (end < self.strlen) and s[end].isalpha():
			end += 1
		# is nil
		if s[beg:end] == 'nil':
			return None, end
		# is true
		elif s[beg:end] == 'true':
			return True, end
		# is false
		elif s[beg:end] == 'false':
			return False, end
		# error
		else:
			raise LuaError()

	def parseShortcut(self, s, beg):
		end = beg
		while (end < self.strlen) and self.isShortcut(s[end]):
			end += 1
		return s[beg:end], end

	def parseValue(self, s, beg):
		# escape whitespace and lua comment
		beg = self.escape(s, beg)
		self.check(beg)
		if s[beg] == '{':
			return self.parseTable(s, beg)
		elif s[beg] == 'n' or s[beg] == 't' \
		or s[beg] == 'f':
			return self.parseConstant(s, beg)
		elif self.equals(s, beg, beg+2, "[[") or \
		s[beg] == "'" or s[beg] == '"' or \
		("-0123456789.".find(s[beg]) > -1):
			return self.parseString(s, beg)
		else:
			raise LuaError()

	def dumpNone(self):
		return "nil"

	def dumpBool(self, v):
		if v == True:
			return "true"
		else:
			return "false"

	def dumpNumber(self, v):
		return str(v)

	def dumpString(self, v):
		escapeList = {
			"\a": "\\a",
			"\b": "\\b",
			"\f": "\\f",
			"\n": "\\n",
			"\r": "\\r",
			"\t": "\\t",
			"\v": "\\v",
			"\"": '\\"',
			"\'": "\\'",
			"\\": "\\\\"
		}
		"""
		if isinstance(v, unicode):
			v = v.encode("utf-8")
		"""
		li = []
		for c in v:
			if c in escapeList:
				li.append(escapeList[c])
			else:
				li.append(c)
		s = "".join(li)
		if s.find('"') > -1:
			return "'" + s + "'"
		else:
			return '"' + s + '"'

	def dumpList(self, v):
		li = []
		for e in v:
			li.append(self.dumpValue(e))
		return "{" + ",".join(li) + "}"

	def dumpTable(self, v):
		li = []
		for key, val in v.iteritems():
			if isinstance(key, tuple) or isinstance(key, complex):
				raise PyError()
			if isinstance(val, tuple) or isinstance(val, complex):
				raise PyError()
			li.append("[" + self.dumpValue(key) + "]=" + self.dumpValue(val))
		return "{" + ",".join(li) + "}"

	def dumpValue(self, v):
		# is None
		if v == None:
			return self.dumpNone()
		# is bool
		elif isinstance(v, bool):
			return self.dumpBool(v)
		# is str
		elif self.isString(v):
			return self.dumpString(v)
		# is list
		elif isinstance(v, list):
			return self.dumpList(v)
		# is dict 
		elif isinstance(v, dict):
			return self.dumpTable(v)
		elif self.isNumber(v):
			return self.dumpNumber(v)
		else:
			raise PyError()

	def dump(self):
		return self.dumpValue(self.data)

	def loadLuaTable(self, f):
		li = []
		fp = None
		try:
			fp = open(f, "r")
		except:
			raise FpError()
		try:
			li = fp.readlines()
		except:
			raise FpError()
		finally:
			fp.close()
		s = "".join(li)
		self.load(s)

	def dumpLuaTable(self, f):
		fp = None
		try:
			fp = open(f, "w")
		except:
			raise FpError()
		lua_tbl = self.dump()
		try:
			fp.write(lua_tbl)
		except:
			raise FpError()
		finally:
			fp.close()

	def loadValue(self, v):
		if isinstance(v, list):
			li = []
			for e in v:
				li.append(self.loadValue(e))
			return li
		elif isinstance(v, dict):
			di = {}
			for k, e in v.iteritems():
				di[k] = self.loadValue(e)
			return di
		else:
			return v

	def loadDict(self, d):
		di = {}
		if isinstance(d, list):
			for k, v in enumerate(d):
				di[k] = self.loadValue(v)
		elif isinstance(d, dict):
			for k, v in d.iteritems():
				if self.isString(k) or self.isNumber(k):
					di[k] = self.loadValue(v)
		self.data = di
	
	def dumpDict(self):
		di = {}
		if isinstance(self.data, list):
			for k, v in enumerate(self.data):
				di[k] = self.loadValue(v)
		elif isinstance(self.data, dict):
			for k, v in self.data.iteritems():
				di[k] = self.loadValue(v)
		return di

if __name__ == "__main__":
	"""
	a = PyLuaTblParser()
	test_str = '{array = {65,23,5,},dict = {mixed = {43,54.33,false,9,string = "value",},array = {3,6,4,},string = "value",},}'
	import json
	a.load(test_str)
	print "loaded lua table", json.dumps(a.data)
	test_str1 = a.dump()
	print "dumped lua table", test_str1
	b = PyLuaTblParser()
	b.load(test_str1)
	print "loaded lua table", json.dumps(b.data)
	print b.dumpDict()
	test_str2 = '{x=-0xffp-2, y=45;--[[adsfasdf]==]asdfasfd--]]"a", "one", "two\\n", "three",[2]=3}'
	a.load(test_str2)
	print "loaded lua table", json.dumps(a.data)
	"""
	import json
	a1 = PyLuaTblParser()
	a2 = PyLuaTblParser()
	a3 = PyLuaTblParser()
	test_str = '{array = {65,23,5,},dict = {mixed = {43,54.33,false,9,string = "value",},array = {3,6,4,},string = "value",},}'
	a1.load(test_str)
	d1 = a1.dumpDict()
	a1.loadDict(d1)
	# a2.dumpLuaTable("error.txt")
	a3.loadLuaTable("error.txt")
	d3 = a3.dumpDict()
