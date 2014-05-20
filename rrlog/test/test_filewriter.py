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
@summary:
Test file writer/ file rotation.
Requires py.test from the PyPy project.
@author: Ruben Reifenberg
"""


from rrlog import *
from rrlog.server import *
from rrlog.server.filewriter import FileLogWriter



def logSequence(rotateCount=3, rotateLineMin=10, lineCount=25, msg="msg<%d>", observers=(), errorLines=(), drop=True, kwargs={}):
	"""
	:param errorLines: list of linenumbers where an error is logged (0==first line)
	"""
	try: assert max(errorLines)<lineCount,"impossible errorLines %s when only %d lines are logged"%(errorLines,lineCount)
	except ValueError: pass

	from rrlog.server.filewriter import createLocalLog # local == all in same process, no log server
	import rrlog
	ORIG = rrlog.server.filewriter.LOGWRITER_CLASS
	rrlog.server.filewriter.LOGWRITER_CLASS = FakeFileLogWriter
	log = createLocalLog(
		filePathPattern = "logfile_%s",  # "pattern" because %s (or %d) is required for the rotate-number
		rotateCount=rotateCount,
		rotateLineMin=rotateLineMin,
		observers=observers,
		drop=drop,
		**kwargs
		)

	# now, log some lines:
	for i in range(0,lineCount):
		print("logging msg:%s,lineCount=%d"%(msg%(i),lineCount))
		if i in errorLines:
			log(msg%(i),"E")
		else:
			log(msg%(i))
	rrlog.server.filewriter.LOGWRITER_CLASS = ORIG
	return log



def test_f_112():
	"""
	cover log writing and  rotation
	"""
	FakeFile.reset()
	log = logSequence(rotateCount=1, rotateLineMin=1, lineCount=2)
	# The server has a rotate-writer, containing rotateCount single-table writers,
	# and each of these has one table:
	fs = FakeFile.instances
	assert len(fs) == 2 #old 3
	assert fs[0][0] == fs[1][0] # same config again
	assert len(fs[0][1].lines) == 1 # lines in first file
	assert len(fs[1][1].lines) == 1 # lines in second file
	#assert len(fs[2][1].lines) == 0 # lines in current file #old: 0 lines - file

	# right line content?
	assert "msg<0>" in fs[0][1].lines[0]
	assert "msg<1>" in fs[1][1].lines[0]

def test_f_122():
	FakeFile.reset()
	#consider: use rotateLineCount as rotateLineMin+1
	log = logSequence(rotateCount=1, rotateLineMin=2, lineCount=2)
	fs = FakeFile.instances
	assert len(fs) == 1 # old 2
	assert len(fs[0][1].lines) == 2 # lines in first file

def test_f_123():
	FakeFile.reset()
	log = logSequence(rotateCount=1, rotateLineMin=2, lineCount=3)
	fs = FakeFile.instances
	assert len(fs) == 2
	assert fs[0][0] == fs[1][0] # same config again
	assert len(fs[0][1].lines) == 2 # lines in first file
	assert len(fs[1][1].lines) == 1 # lines in second file

def test_f_223():
	FakeFile.reset()
	log = logSequence(rotateCount=2, rotateLineMin=2, lineCount=3)
	fs = FakeFile.instances
	assert len(fs) == 2
	assert fs[0][0] != fs[1][0]
	assert len(fs[0][1].lines) == 2 # lines in first file
	assert len(fs[1][1].lines) == 1 # lines in second file

	# right line content?
	assert "msg<0>" in fs[0][1].lines[0]
	assert "msg<1>" in fs[0][1].lines[1]
	assert "msg<2>" in fs[1][1].lines[0]


def test_f_2x3_catsEnable():
	FakeFile.reset()
	log = logSequence(rotateCount=2, rotateLineMin=77, lineCount=3, errorLines=(0,2), kwargs={"catsEnable":("E",)} )
	fs = FakeFile.instances
	assert len(fs) == 1
	assert len(fs[0][1].lines) == 2 # lines in first file

	# right line content?
	assert "msg<0>" in fs[0][1].lines[0]
	# msg1 is no "E" -> skipped
	assert "msg<2>" in fs[0][1].lines[1]


def test_f_2x3_catsDisable():
	FakeFile.reset()
	log = logSequence(rotateCount=2, rotateLineMin=77, lineCount=3, errorLines=(0,2), kwargs={"catsDisable":("E",)} )
	fs = FakeFile.instances
	assert len(fs) == 1
	assert len(fs[0][1].lines) == 1 # lines in first file

	# right line content?
	assert "msg<1>" in fs[0][1].lines[0]
	# msg0,msg2 is "E" -> skipped


def test_f_norotation():
	FakeFile.reset()
	log = logSequence(rotateCount=1, rotateLineMin=None, lineCount=77)
	fs = FakeFile.instances
	assert len(fs) == 1
	assert len(fs[0][1].lines) == 77 # lines in first file

	# right line content?
	assert "msg<0>" in fs[0][1].lines[0]
	assert "msg<1>" in fs[0][1].lines[1]
	assert "msg<76>" in fs[0][1].lines[76]


def test_f_100_10_1000():
	"""higher numbers to cover job reusage (job pooling)"""
	FakeFile.reset()
	log = logSequence(rotateCount=100, rotateLineMin=10, lineCount=1001)
	fs = FakeFile.instances
	assert len(fs) == 101
	assert fs[0][0] != fs[1][0]
	assert fs[0][0] != fs[99][0]
	assert fs[0][0] == fs[100][0] # the first writer is used again
	assert len(fs[0][1].lines) == 10 # lines in first file
	assert len(fs[100][1].lines) == 1 # old 0 # lines in latest

	# right line content?
	assert "msg<0>" in fs[0][1].lines[0]
	assert "msg<9>" in fs[0][1].lines[9]
	assert "msg<990>" in fs[99][1].lines[0]
	assert "msg<999>" in fs[99][1].lines[9]
	assert "msg<1000>" in fs[100][1].lines[0]




def test_format_line():
	"""
	format_line argument
	"""
	FakeFile.reset()
	log = logSequence(rotateCount=1, rotateLineMin=1, lineCount=2, kwargs={"format_line":lambda job,lineCount:"X%sX"%(job.msg)})
	# The server has a rotate-writer, containing rotateCount single-table writers,
	# and each of these has one table:
	fs = FakeFile.instances

	# right line content?
	assert fs[0][1].lines[0] == "Xmsg<0>X"
	assert fs[1][1].lines[0] == "Xmsg<1>X"



class FakeFile(object):
	@classmethod
	def reset(cls):
		cls.instances = []
	instances = []
	def __init__(self, config):
		print("new FakeFile:%s"%(config))
		self.lines = []
		self.__class__.instances.append( (config,self) )
	def flush(self): pass
	def close(self): pass
	def write(self, line):
		print("%s:Append line:%s"%(self,line))
		self.lines.append(line)
	def __repr__(self): return "FakeFile[%d lines]"%(len(self.lines))


class FakeFileLogWriter(FileLogWriter):
	"""
	"""
	def _createFile(self):
		print("================> test_filewriter: make FakeFile")
		self._logfile = FakeFile(self._config)


if __name__ == "__main__":
	import sys
	from rrlog.test import run
	#run(sys.argv[0],k="test_indi")
	run(sys.argv[0])
