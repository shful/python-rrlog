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
Test both observer & filter functionality
@author: Ruben Reifenberg
"""


from rrlog import *
from rrlog.server import *
from rrlog.test.test_printwriter import logSequence,FakeFile


class Checker(object):
	def __init__(self, expected_msgs, raiseon=None):
		"""
		:param raiseon: raise ValueError when that message appears (==simulate internal error)
		"""
		self.i = 0
		self.expected_msgs = expected_msgs
		self.raiseon = raiseon
		
	def __call__(self, jobhist, writer):
		job = jobhist[-1]
		print "__call__ %s in %d.%s"%(job.msg, self.i, self.__class__.__name__)
		assert job.msg == self.expected_msgs[self.i]		
		self.i += 1
		if self.raiseon == job.msg:
			raise ValueError("You told me to raise on %s"%(self.raiseon))
	def assert_finished(self):
		assert self.i == len(self.expected_msgs)

		
class LegacyObserver(Checker):
	""" same but with observe() methode instead __call__() """
	def __call__(self, *args, **kwargs):
		assert False, "expected observe() to be called"
		
	def observe(self, *args, **kwargs):
		print "observe called"
		Checker.__call__(self, *args, **kwargs)
	
def format_line(job):
	return job.cat+"***"+job.msg


def test_observers():
	""" observers added and called ? """
	FakeFile.reset()
	#consider: use rotateLineCount as rotateLineMin+1
	msgs = ("msg<0>","msg<1>")
	checkers = (Checker(msgs),LegacyObserver(msgs)) 
	log = logSequence(
		lineCount=2, 
		kwargs={"observers":checkers}
		)
	for i,checker in enumerate(checkers):
		print "checker %d finished?"%(i)
		checker.assert_finished()
	fs = FakeFile.instances
	assert len(fs) == 1 # old 2
	assert len(fs[0].lines) == 2 # lines in first file

#def test_observers_error():
#	""" Handling of internal error in an observer """
#	FakeFile.reset()
#	#consider: use rotateLineCount as rotateLineMin+1
#	msgs = ("msg<0>","msg<1>")
#	checkers = (Checker(msgs, raiseon="msg<1>"),LegacyObserver(msgs))
#	
#	def modifylog(x):
#		""" switch off observe internal error """
#		x._server.oie=False
#		
#	log = logSequence(
#		lineCount=2, 
#		modifylog=modifylog,
#		kwargs={"observers":checkers,"format_line":format_line}
#		)
#	
#	for i,checker in enumerate(checkers):
#		print "checker %d finished?"%(i)
#		checker.assert_finished()
#		
#	fs = FakeFile.instances
#	
#	assert len(fs) == 1
#	assert len(fs[0].lines) == 3 # includes an error line
#	assert fs[0].lines[2].startswith("I***") # indicates Internal error, format_line writes cat+"***" ...
	
	
def test_filters():
	""" filters added and called ? """
	FakeFile.reset()
	#consider: use rotateLineCount as rotateLineMin+1
	msgs = ("msg<0>","msg<1>")
	checkers = (Checker(msgs),) 
	log = logSequence(
		lineCount=2, 
		kwargs={"filters":checkers}
		)
	for i,checker in enumerate(checkers):
		print "checker %d finished?"%(i)
		checker.assert_finished()
	fs = FakeFile.instances
	assert len(fs) == 1 # old 2
	assert len(fs[0].lines) == 2 # lines in first file
	
	


if __name__ == "__main__":
	import sys
	from rrlog.test import run
	#run(sys.argv[0],k="test_observers_error")
	run(sys.argv[0])
