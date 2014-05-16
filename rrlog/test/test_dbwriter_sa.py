# Copyright (c) 2007 Ruben Reifenberg.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#    
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
@requires: SQLAlchemy 0.4.0 and compatible
@summary:
Test problem archiver. Disable this test when SQLAlchemy is not available.
@author: Ruben Reifenberg
"""


from rrlog import *
from rrlog.server import *


# sqlite is easier test setup but sometimes problematic with parallel tests
# In mysql, prepare
# create database logtest
# grant all on logtest.* to logtester

engineStr = "mysql://logtester@localhost/logtest"
#engineStr = 'sqlite:///:memory:'


from sqlalchemy import create_engine
try:
	from sqlalchemy import __version__
	print __version__
except ImportError:
	print "very old SqlAlchemy ?"


def logTables(log):
	"""
	"""
	return [w.getTable() for w in log._server._writer.writers]


def logSequence(rotateCount=3, rotateLineMin=10, lineCount=25, msg="msg%d", observers=(), errorLines=(), drop=True, kwargs={}):
	"""
	:param errorLines: list of linenumbers where an error is logged (0==first line)
	"""
	engine = create_engine(engineStr)
	c = engine.connect()
	
	try:
		assert max(errorLines)<lineCount,"impossible errorLines %s when only %d lines are logged"%(errorLines,lineCount)
	except ValueError: pass

	from rrlog.server.dbwriter_sa import createLocalLog # local == all in same process, no log server

	log = createLocalLog(
		engineStr = engineStr,
		tableNamePattern = "logtable_%s",  # "pattern" because %s (or %d) is required for the rotate-number
		rotateCount=rotateCount,
		rotateLineMin=rotateLineMin,
		observers=observers,
		drop=drop,
		**kwargs
		)

	# now, log some lines:
	for i in range(0,lineCount):
		if i in errorLines:
			log(msg%(i),"E")
		else:
			log(msg%(i))
			
	return log


def test_log_SA_112():
	"""
	cover log writing and  rotation
	"""
	log = logSequence(rotateCount=1, rotateLineMin=1, lineCount=2)
	# The server has a rotate-writer, containing rotateCount single-table writers,
	# and each of these has one table:
	tables = logTables(log)
	assert len(tables) == 1
	
	engine = create_engine(engineStr)
	c = engine.connect()	
	# after each single line, the rotation deletes everything:
	assert len( [x for x in c.execute(tables[0].select())] ) == 1 #old 0


def test_log_SA_122():
	log = logSequence(rotateCount=1, rotateLineMin=2, lineCount=2)
	tables = logTables(log)
	assert len(tables) == 1

	engine = create_engine(engineStr)
	c = engine.connect()		
	# after 2 lines, the rotation deletes everything:
	assert len( [x for x in c.execute(tables[0].select())] ) == 2 #old 0


def test_log_SA_123():
	log = logSequence(rotateCount=1, rotateLineMin=2, lineCount=3)
	tables = logTables(log)
	assert len(tables) == 1

	engine = create_engine(engineStr)
	c = engine.connect()	
	# after 2 lines, the rotation deletes everything, and 1 line is written.
	assert len( [x for x in c.execute(tables[0].select())] ) == 1

def test_log_SA_173_catsEnable():
	log = logSequence(rotateCount=1, rotateLineMin=7, lineCount=3,errorLines=(0,),kwargs={"catsEnable":("E",)})
	tables = logTables(log)
	assert len(tables) == 1

	engine = create_engine(engineStr)
	c = engine.connect()	
	assert len( [x for x in c.execute(tables[0].select())] ) == 1 #only "E" - line 0

def test_log_SA_173_catsDisable():
	log = logSequence(rotateCount=1, rotateLineMin=7, lineCount=3,errorLines=(0,),kwargs={"catsDisable":("E",)})
	tables = logTables(log)
	assert len(tables) == 1

	engine = create_engine(engineStr)
	c = engine.connect()	
	assert len( [x for x in c.execute(tables[0].select())] ) == 2 #without "E" - line 0


def test_log_SA_123_nodrop_norotation():
	log = logSequence(rotateCount=1, rotateLineMin=None, lineCount=3)
	tables = logTables(log)
	assert len(tables) == 1
	
	engine = create_engine(engineStr)
	c = engine.connect()		
	assert len( [x for x in c.execute(tables[0].select())] ) == 3

	# no drop:
	log = logSequence(rotateCount=1, rotateLineMin=None, lineCount=4, drop=False)
	tables = logTables(log)
	assert len(tables) == 1

	engine = create_engine(engineStr)
	c = engine.connect()		
	assert len( [x for x in c.execute(tables[0].select())] ) == 3+4


def test_log_SA_123_drop_norotation():
	# drop and start with empty one:
	log = logSequence(rotateCount=1, rotateLineMin=None, lineCount=4, drop=True)
	tables = logTables(log)
	assert len(tables) == 1

	engine = create_engine(engineStr)
	c = engine.connect()		
	assert len( [x for x in c.execute(tables[0].select())] ) == 4


def test_log_SA_223():
	log = logSequence(rotateCount=2, rotateLineMin=2, lineCount=3)
	tables = logTables(log)
	assert len(tables) == 2
	
	engine = create_engine(engineStr)
	c = engine.connect()	
	# 2 lines in oldest, and 1 line in current table:
	assert len( [x for x in c.execute(tables[0].select())] ) == 2
	assert len( [x for x in c.execute(tables[1].select())] ) == 1


def test_individual_cols():
	"""
	individual str + int column is added
	"""
	from rrlog.server.dbwriter_sa import createLocalLog,DBConfig # local == all in same process, no log server

	cols = list(DBConfig.COLS_DEFAULT) +[
			("my_int",DBConfig.Integer),
			]
	cols.insert(1,("my_str",DBConfig.String(5),{"default":"my default for my_str"}))
	log = createLocalLog(
		engineStr = engineStr,
		tableNamePattern = "logtable_%s",  # "pattern" because %s (or %d) is required for the rotate-number
		rotateCount=1,
		rotateLineMin=1000,
		drop=True,
		cols=cols,
		)
	msg = "individual_cols_msg%d"
	lineCount = 33
	errorLines = (1,6)
	# now, log some lines:
	for i in range(0,lineCount):
		if i in errorLines:
			log(msg%(i),"E",my_int=i+33,my_str="%02d-Hello"%(i))
		else:
			log(msg%(i),my_int=i+33,my_str="%02d-Hello"%(i))

	tables = logTables(log)
	assert len(tables) == 1

	engine = create_engine(engineStr)
	c = engine.connect()	
	# after each single line, the rotation deletes everything:
	for i,x in enumerate(c.execute(tables[0].select())):
		assert x["msg"]==msg%(i),"%d:got: %s,table=%s"%(i,x,tables[0])
		assert x["my_int"]==i+33
		assert x["my_str"]=="%02d-He"%(i)#maxchars=5
	assert i==32 #0..32


def test_individual_cols_defaultvalues():
	"""
	individual str + int column is added
	"""
	from rrlog.server.dbwriter_sa import createLocalLog,DBConfig # local == all in same process, no log server

	cols = list(DBConfig.COLS_DEFAULT) +[
			("my_int",DBConfig.Integer),
			]
	cols.insert(1,("my_str",DBConfig.String(5)))
	log = createLocalLog(
		engineStr = engineStr,
		tableNamePattern = "logtable_%s",  # "pattern" because %s (or %d) is required for the rotate-number
		rotateCount=1,
		rotateLineMin=1000,
		drop=True,
		cols=cols,
		)
	msg = "individual_cols_msg%d"
	lineCount = 50
	errorLines = (1,6)
	# now, log some lines using default values for both the new cols:
	for i in range(0,lineCount):
		if i in errorLines:
			log(msg%(i),"E")
		else:
			log(msg%(i))

	tables = logTables(log)
	assert len(tables) == 1

	engine = create_engine(engineStr)
	c = engine.connect()	
	# after each single line, the rotation deletes everything:
	for i,x in enumerate(c.execute(tables[0].select())):
		assert x["msg"]==msg%(i)
		assert x["my_int"]==None
		assert x["my_str"]==None
	assert i==lineCount-1


if __name__ == "__main__":
#	import sys
#	for x in sys.path: print x
	from rrlog.test import run
	#run(sys.argv[0],k="test_log_SA_123_")
	run(sys.argv[0])
