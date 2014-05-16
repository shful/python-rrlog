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
Test core functionality, Log and LogServer (not the XMLRPC part).
Requires py.test from the PyPy project.
@author: Ruben Reifenberg
"""


import re
from rrlog import *
from rrlog.server import *


def line_xFunction(callable, *args, **kwargs):
	return callable(*args, **kwargs)

def line_yFunction(callable, *args, **kwargs):
	return line_xFunction(callable, *args, **kwargs)

def thisfname():
	"""
	:returns: my filename without path and without py
	"""
	assert __name__ is not "__main__"
	return __name__.split(".")[-1]

class AttrDict(dict):
	def __init__(self, target):
		dict.__init__(self, **target)
		self.target=target
	def __getattr__(self, key):
		return self.target[key]

class _TestLogWriter(object):
	clientid=None
	msgid=1
	currDict=None
	fnMatch=None
	stackCheckLimit=777 # can we compare the path with LINE_X and LINE_Y ?
	thisfnameOccurrences=(0,777) # this file must appear >=0 and <777 times in the stack path
	clnExpected=None # the expected cln of any job, -1 means don't check
	def writeNow(self, job):
		clnExpected = self.clnExpected
		if clnExpected is None: clnExpected=LINE_X # default to the line-x-function
		d = AttrDict(self.currDict)
		assert job.msg==d.msg
		if "cat" in d: assert job.cat==d.cat
		if "special" in d: assert job.special==d.special
		if self.stackCheckLimit==0:
			# no cfn,cln available
			assert job.cfn() is None,"cfn was %s."%(job.cfn())
			assert job.cln()==-1,"cln was %s"%(job.cln())
		if self.stackCheckLimit>=1:
			print "CFN = %s, path=%s."%(job.cfn(), job.path)
			assert self.fnMatch.match(job.cfn()) is not None,"cfn was %s,%s"%(job.cfn(),type(job.cfn()))
			if clnExpected >=0:
				assert job.cln()==clnExpected,"cln was %s not %s"%(job.cln(),clnExpected)
		if self.stackCheckLimit>=2:
			#path[1][0] is my filename but not formatted, like cfn() was.
			assert job.path[1][1]==LINE_Y,"cln[1] was %s not %s"%(job.path[1][1],LINE_Y)
		assert job.msgid==self.msgid, "msgid was %s, not %s."%(job.msgid,self.msgid)

		# for seFilesExclude check: is my filename removed out of path? :
#		assert job.cfn() is None or self._count_cfn_in_path(job.cfn(), path=job.path) >= self.thisfnameOccurrences[0]
#		assert job.cfn() is None or self._count_cfn_in_path(job.cfn(), path=job.path) < self.thisfnameOccurrences[1]
		assert self._count_cfn_in_path(thisfname(), path=job.path) >= self.thisfnameOccurrences[0]
		assert self._count_cfn_in_path(thisfname(), path=job.path) < self.thisfnameOccurrences[1]

	def _count_cfn_in_path(self, cfn, path):
		"""
		:returns: how many filenames f are in path where cfn is substring of f ? 
		:rtype: int >= 0
		"""
		res = 0
		for elem in path:
			# Since 0.2.0: "is not None" required,filename is not omitted but None now
			if (elem[0] is not None) and elem[0].find(cfn) > 0:
				res += 1
		return res

class TestLogAndServer(object):
	def log(self, msg, **kwargs): #expect everything but msg as kwarg
		self.w.currDict=kwargs.copy()
		self.w.currDict["msg"]=msg
		line_yFunction(self.l, msg, **kwargs)

	def _test1(self):
		# Client 1
		self.l = Log(server=self.s, stackMax=4)
		self.s._cfnMode=self.s.CFN_SHORT
		self.w.fnMatch=re.compile("^"+thisfname()+"$")
		print "name=%s"%(__name__)
		self.log("msg1",cat="T")

	def _test2(self):
		self.s._cfnMode=self.s.CFN_FULL
		self.w.msgid=2
		self.w.fnMatch=re.compile(".*"+__name__+"-py$")
		self.log("msg2")

	def _test3(self):
		# Client 2
		self.l = Log(server=self.s, stackMax=4)
		self.w.clientid=2
		self.w.msgid=1
		self.log("msg3",cat=None, special={"abc":""})

	def _test4(self):
		# Client 3
		self.l = Log(server=self.s, stackMax=0)
		self.w.stackCheckLimit=0
		self.log("msg4")

	def _test5(self):
		# Client 3
		self.l = Log(server=self.s, msgCountLimit=3, stackMax=4)
		self.w.stackCheckLimit=2
		self.w.msgid=1
		self.log("msg5-1")
		self.w.msgid=2
		self.log("msg5-2")
		self.w.msgid=1 # back to 1 since limit was 3
		self.log("msg5-3")

	def test_12345(self):
		#_testN() are one test, i.e. they need their order
		# the order checks that both msgid and clientid are counted up
		cls = self.__class__
		cls.w = _TestLogWriter()
		cls.s = LogServer(writer=cls.w)
		self._test1()
		self._test2()
		self._test3()
		self._test4()
		self._test5()

	def test_seFilesExclude(self):
		cls = self.__class__
		cls.w = _TestLogWriter()
		cls.s = LogServer(writer=cls.w)

		# Client 1
		# 1.without valid seFilesExclude
		self.l = Log(server=self.s, stackMax=777, seFilesExclude=re.compile("doesnotexist.*").search )
		self.w.thisfnameOccurrences=(4,777) # because seFilesExclude excludes nothing
		self.s._cfnMode=self.s.CFN_SHORT
		self.w.fnMatch=re.compile("^"+thisfname()+"$")
		print "name=%s"%(__name__)
		self.log("msg1",cat="T")


		# 2.with valid seFilesExclude
		cls = self.__class__
		cls.w = _TestLogWriter()
		cls.s = LogServer(writer=cls.w)

		# Client 1
		# need high stackMax because seFilesExclude may reduce the stack length near 0 otherwise:
		self.l = Log(server=self.s, stackMax=777, seFilesExclude=re.compile("test_core.*").search )
		self.w.stackCheckLimit = 1 # because the stacktrace is "manipulated" by seFilesExclude, which would erroneously alert the test.
		self.w.thisfnameOccurrences=(0,1) # because seFilesExclude excludes this filename completely
		self.s._cfnMode=self.s.CFN_SHORT
		self.w.clnExpected = -1
#		self.w.fnMatch=re.compile("^"+__name__.split(".")[-1]+"$") #since 0.2.1,even the clf/cfn is excluded by seFilesExclude:this file should not appear anymore in the path
		self.w.fnMatch=re.compile("^.*[^"+thisfname()+"].*$") #anything but my filename
		print "name=%s"%(__name__)
		self.log("msg1",cat="T")

	def test_traceOffset(self):
		cls = self.__class__
		cls.w = _TestLogWriter()
		cls.s = LogServer(writer=cls.w)

		# 1. traceOffset 1
		self.l = Log(server=self.s, traceOffset=1, stackMax=777)
		self.w.fnMatch=re.compile("^"+thisfname()+"$")
		self.w.clnExpected=LINE_Y # because traceOffset, line-x is omitted
		self.w.stackCheckLimit=1 # don't check path[1] (usually, with no traceOffset, it is line-y) 
		print "name=%s"%(__name__)
		self.log("msg1",cat="T")

		# 2. invalid, huge traceOffset
		# required not to crash, nothing else
		self.l = Log(server=self.s, traceOffset=4444, stackMax=777)
		self.w.stackCheckLimit=-1 # don't check cfn/cln, its undefined with that high offset 
		self.log("msg1",cat="T")
		



def setup_module(module):
	global LINE_X # the line in this source file where line_xFunction calls the callable.
	global LINE_Y # the line in this source file where line_yFunction calls the callable.
	file__ = __file__.replace("pyc","py") # HACK we need the source file, no matter how the test is run
	this = open(file__,"r") # not file(). open seems to be kept with Py3k
	for i,line in enumerate(this):
		if line.startswith("def line_xFunction"):
			LINE_X = i+2
		if line.startswith("def line_yFunction"):
			LINE_Y = i+2
	this.close()
	assert LINE_X>0
	assert LINE_Y>0



if __name__ == "__main__":
	import sys
	from rrlog.test import run
	#run(sys.argv[0],k="test_indi")
	run(sys.argv[0])
