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
Test print writer (analogous to file writer test)
@author: Ruben Reifenberg
"""


from rrlog import *
from rrlog.server import *



def logSequence(lineCount=25, msg="msg<%d>", errorLines=(), drop=True, modifylog=None, kwargs={}):
	"""
	:param errorLines: list of linenumbers where an error is logged (0==first line)
	"""
	try: assert max(errorLines)<lineCount,"impossible errorLines %s when only %d lines are logged"%(errorLines,lineCount)
	except ValueError: pass

	from rrlog.server.printwriter import createLocalLog # local == all in same process, no log server
	import rrlog
	#FakeFile.reset()
	ff = FakeFile()

	log = createLocalLog(
		**kwargs
		)
	
	if modifylog is not None:
		modifylog(log)

	rrlog.server.printwriter.print_ = ff.write
	# now, log some lines:
	for i in range(0,lineCount):
		print "logging msg:%s,lineCount=%d"%(msg%(i),lineCount)
		if i in errorLines:
			log(msg%(i),"E")
		else:
			log(msg%(i))
			
	return log


	

def test_f_122():
	FakeFile.reset()
	#consider: use rotateLineCount as rotateLineMin+1
	log = logSequence(lineCount=2)
	fs = FakeFile.instances
	assert len(fs) == 1 # old 2
	assert len(fs[0].lines) == 2 # lines in first file


def test_f_2x3_catsEnable():
	FakeFile.reset()
	log = logSequence(lineCount=3, errorLines=(0,2), kwargs={"catsEnable":("E",)} )
	fs = FakeFile.instances
	assert len(fs) == 1
	assert len(fs[0].lines) == 2 # lines in first file

	# right line content?
	assert "msg<0>" in fs[0].lines[0]
	# msg1 is no "E" -> skipped
	assert "msg<2>" in fs[0].lines[1]


def test_f_2x3_catsDisable():
	FakeFile.reset()
	log = logSequence(lineCount=3, errorLines=(0,2), kwargs={"catsDisable":("E",)} )
	fs = FakeFile.instances
	assert len(fs) == 1
	assert len(fs[0].lines) == 1 # lines in first file

	# right line content?
	assert "msg<1>" in fs[0].lines[0]
	# msg0,msg2 is "E" -> skipped




def test_f_100_10_1000():
	"""higher numbers to cover job reusage (job pooling)"""
	FakeFile.reset()
	log = logSequence(lineCount=1001)
	fs = FakeFile.instances
	assert len(fs) == 1

	# right line content?
	assert "msg<0>" in fs[0].lines[0]
	assert "msg<9>" in fs[0].lines[9]
	assert "msg<990>" in fs[0].lines[990]
	assert "msg<999>" in fs[0].lines[999]
	assert "msg<1000>" in fs[0].lines[1000]




def test_format_line():
	"""
	format_line argument
	"""
	FakeFile.reset()
	log = logSequence(
		lineCount=2,
		kwargs={"format_line":lambda job,lineCount:"X%sX"%(job.msg)}
		)
	# The server has a rotate-writer, containing rotateCount single-table writers,
	# and each of these has one table:
	fs = FakeFile.instances

	# right line content?
	assert fs[0].lines[0] == "Xmsg<0>X"
	assert fs[0].lines[1] == "Xmsg<1>X"



class FakeFile(object):
	@classmethod
	def reset(cls):
		print "[FF]:reset"
		cls.instances = []
	instances = []
	def __init__(self):
		self.lines = []
		self.__class__.instances.append(self)
		print "new FakeFile %s"%(self)
	def flush(self): pass
	def close(self): pass
	def write(self, line):
		print "[FF]%s:write:%s"%(self,line)
		self.lines.append(line)
	def __repr__(self): return "FakeFile%d[%d lines]"%(id(self),len(self.lines))




if __name__ == "__main__":
	import sys
	from rrlog.test import run
	#run(sys.argv[0],k="test_obs")
	run(sys.argv[0])
