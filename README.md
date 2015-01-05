# PyLuaTblParser

## Usage
1. import PyLuaTblParser as P --this import the PyLuaTblParser module
2. parser = P.PyLuaTblParser() --this create a new PyLuaTblParser object
3. parser.load(lua_tbl_str) --this load the lua_tbl_str string to python
   dict or list which stores in parser.data, if the lua_tbl_str is not a 
   valid lua table string, the load function will raise "illegal lua string" 
   error
4. parser.loadLuaTable(file_path) --this load the lua table string in file_path
   to python dict or list(based on the lua table is array or table) as 3 does. 
   if exception occurs duing file operation, the loadLuaTable function will raise
   "python file io exception" error, if the lua table string is not valid, this 
   function will raise the same error as 3
5. lua_tbl_str = parser.dump() --this dump the parser.data to a lua table string
   which stores in lua_tbl_str
6. parser.dumpLuaTable(file_path) --this dump the parser.data to a lua table string 
   in the file which file_path specific, all the previous data in the file will be 
   clear, if exception occurs during the file operation, the dumpLuaTable function 
   will raise "python file io exception" error as 4 does.
7. parser.loadDict(d) --this load the python dict to parser.data, this create a deep 
   copy all the (key, value) pair in d if the k satisfy the condition that it's a 
   number or string, the old value in parser.data will be discard
8. d = parser.dumpDict() --this dump the parser.data to d, this create a deep copy of
   parser.data

## example
###   -- import the PyLuaTblParser
###   import PyLuaTblParser as P
###   parser = P.PyLuaTblParser()
###   teststr = '{array = {65,23,5,},dict = {mixed = {43,54.33,false,9,string = "value",},array = {3,6,4,},string = "value",},}'
###   -- load the teststr to parser.data
###   parser.load(teststr)
###   -- dump the parser.data to teststr1
###   teststr1 = parser.dump()
###   -- dump the parser.data to test.txt
###   parser.dumpLuaTable("test.txt")
###   -- load the lua table string from test.txt
###   parser.loadLuaTable("test.txt")
###   d = {1: 'a', 2: 'one', 3: 'two', 4: 'three', 'y': 45, 'x': -63.75}
###   -- load the dict d to parser.data, the old value in parser.data will be discard
###   parser.loadDict(d)
###   -- dump the parser.data to d,
###   d = parser.dumpDict()


