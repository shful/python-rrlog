
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
Test line indention by stack depth
Requires py.test from the PyPy project.
@author: Ruben Reifenberg
"""


from rrlog.contrib import stackindent
from rrlog.test.test_filewriter import FakeFile,FakeFileLogWriter


def f5(log):
	log("f5")

def f4(log):
	log("f4")
	log("f4",stackindent_tara=-2)
	f5(log)

def f3(log):
	log("f3",stackindent_tara=0)

def f2(log):
	log("f2")
	f3(log)

def f1(log):
	log("f1")
	f2(log)

def fp3(log):
	log("fp3")
	log("$fp3_indented")

def fp2(log):
	log("fp2")
	log("$fp2_indented")
	fp3(log)

def fp1(log):
	log("fp1",stackindent_tara=-77) #tara ignored
	fp2(log)


def format_line(job, lineCount):
	return job.msg	


def create(msgPrefix=None):
	"""
	"""	
	from rrlog.server.filewriter import createLocalLog # local == all in same process, no log server
	import rrlog
	rrlog.server.filewriter.LOGWRITER_CLASS = SimpleFileLogWriter
	log = createLocalLog(
		filePathPattern = "logfile_%s",  # "pattern" because %s (or %d) is required for the rotate-number
		rotateCount=1,
		rotateLineMin=777,
		tsFormat=None,
		drop=True,
		filters=(stackindent.StackIndentFilter(token="%",msgPrefix=msgPrefix),),
		format_line=format_line,
		)
	return log


def test_tara_0():
	"""
	"""
	FakeFile.reset()
	log = create()
	f1(log)
	fs = FakeFile.instances
	assert len(fs) == 1
	assert len(fs[0][1].lines) == 3

	# right line content?
	assert fs[0][1].lines[0]=="f1"
	assert fs[0][1].lines[1]=="%f2"
	assert fs[0][1].lines[2]=="f3"

def test_tara_m2():
	"""
	"""
	FakeFile.reset()
	log = create()
	f4(log)
	fs = FakeFile.instances
	assert len(fs) == 1
	assert len(fs[0][1].lines) == 3

	# right line content?
	assert fs[0][1].lines[0] == "f4"
	assert fs[0][1].lines[1] == "%%f4"
	assert fs[0][1].lines[2] == "%%%f5"


def test_msgPrefix():
	"""
	"""
	FakeFile.reset()
	log = create(msgPrefix="$")
	fp1(log)
	fs = FakeFile.instances
	assert len(fs) == 1
	assert len(fs[0][1].lines) == 5

	# right line content?
	assert fs[0][1].lines[0]=="fp1"
	assert fs[0][1].lines[1]=="fp2"
	assert fs[0][1].lines[2]=="$fp2_indented"
	assert fs[0][1].lines[3]=="fp3"
	assert fs[0][1].lines[4]=="%$fp3_indented"



class SimpleFileLogWriter(FakeFileLogWriter):
	def _format_line(self, job):
		"""
		msg only
		"""
		return job.msg


if __name__ == "__main__":
	import sys
	from rrlog.test import run
	#run(sys.argv[0],k="test_indi")
	run(sys.argv[0])
