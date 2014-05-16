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
Covers some of the demo functions.
Requires py.test from the PyPy project.
@author: Ruben Reifenberg
"""


import sys
import re
import os.path



def demopath():
	"""
	find the path to the documentations demo/ directory
	because the files there are part of the tests.
	"""
	p = os.path.abspath(__file__)
	
	# traverse up to the directory probably containing docs/
	for i in range(0,3):
		p = os.path.split(p)[0]
		
	# check wheter doc/ really exists here
	res = os.path.join(p, "docs") # package demo should be inside docs/
	assert os.path.exists(res)
	assert os.path.isdir(res)	
	return res
	

def setup():
	"""
	the demo directory is usually not in sys.path (it's considered to be part of the doc)
	append it 
	"""
	sys.path.append(demopath())
	print demopath(),"exists?",os.path.exists(demopath())


def teardown():
	sys.path.remove(demopath())


class OpenFF(object):
	"""
	fake replacement of the open() function
	"""
	def __init__(self):
		self.d = {}
		print "OpenFFs %d, %s created"%(id(self),self)
	def __call__(self,path, flag):
		from rrlog.test.test_filewriter import FakeFile
		ff = FakeFile(config=path)
		self.d[path] = ff
		print "OpenFF %d : FF added->%s"%(id(self),self.d)
		return ff
	def ff_by_suffix(self, suffix):
		"""
		asserts false when >1 result is found
		:returns: the only item where key ends with suffix
		"""		
		res = None
		for k,v in self.d.items():
			if k.endswith(suffix):
				assert res is None
				res = v
		assert res is not None, "nothing with %s in %s"%(suffix,self.d)
		return res

def regex_for_path(cfunc, fname, demo_cln, restcount, democount, omittedcxn=""):
	"""
	:param restcount: anonymous path components on the right
	:param democount: call count inside fname (incl.cfn)
	:param omittedcxn: cfn/cln replacement when omitted
	"""
	return (
		" :::%s "%(cfunc)
		+"\|%s%s\(%s\)"%(omittedcxn, fname, demo_cln)
		+"(\<-%s\(\d+\)){%d}"%(fname, democount-1)
		+"\<-test_demo\(\d+\)"
#		+ r"(\<-[\w-]+\(\d+\)){%s}$"%(restcount) #[w-]+ instead \w+ because we can have module name "py-test" 
		)
	
		
def test_demo_customlinefiles():
	"""
	nearly like usingFiles
	"""
	import rrlog.server.filewriter
	ffs = OpenFF()
	print "open->%s"%(ffs)
	oldopen = rrlog.server.filewriter.open_
	rrlog.server.filewriter.open_ = ffs
	
	from demo import demo_customlinefiles
	assert len(ffs.d) == 3 # 3 files by rotation
	# right file content ?
	def assert_(msgcount,lines,i):
		s = ("Original message = "
		+r"'customized-line %s'."%(msgcount)
		+" And the ip address is:12345"		
		)
		rex = re.compile(s)
		line = lines[i]
		assert rex.match(line), "\n%s does not match:\n%s\nmsgcount was %d,index was %d"%(line,s,msgcount,i)
		
	ff = ffs.ff_by_suffix("-0.txt")
	assert len(ff.lines)==10
	assert_(0,ff.lines,0)
	assert_(9,ff.lines,9)
	ff = ffs.ff_by_suffix("-1.txt")
	assert len(ff.lines)==10
	assert_(10,ff.lines,0)
	ff = ffs.ff_by_suffix("-2.txt")
	assert len(ff.lines)==6
	assert_(24,ff.lines,4)
	#ignore the last line which is different (obviously, it raised no exception, at least)
	 
	rrlog.server.filewriter.open_ = oldopen
		

	
def test_demo_indentfiles():
	import rrlog.server.filewriter
	ffs = OpenFF()
	oldopen = rrlog.server.filewriter.open_
	rrlog.server.filewriter.open_ = ffs
	
	from demo import demo_indentfiles
	assert len(ffs.d) == 1
	lines = ffs.ff_by_suffix("").lines
	
	print "-----------------"
	for l in lines:
		print l
	print "-----------------"

	s = (
	"^  1\.\[.+\] begin"
	+regex_for_path("<module>", "demo_indentfiles", 63, 1, 1)
	)
	rex = re.compile(s)	
	assert rex.match(lines[0]), "\n%s does not match:\n%s"%(lines[0],s)

	s = (
	"^  2\.\[.+\] --spam here"
	+regex_for_path("spam","demo_indentfiles", 59, 2, 2)
	)
	rex = re.compile(s)	
	assert rex.match(lines[1]), "\n%s does not match:\n%s"%(lines[1],s)

	s = (
	"^  3\.\[.+\] ----egg here"
	+regex_for_path("egg","demo_indentfiles", 56, 3, 3)
	)
	rex = re.compile(s)	
	assert rex.match(lines[2]), "\n%s does not match:\n%s"%(lines[2],s)
	
	assert len(lines) == 3
	rrlog.server.filewriter.open_ = oldopen


def test_demo_indentstdout():
	import rrlog.server.printwriter
	from rrlog.test.test_printwriter import FakeFile
	ff = FakeFile()
	rrlog.server.printwriter.print_ = ff.write
	
	from demo import demo_indentstdout
	lines = ff.lines
	assert lines[0].rstrip() == "begin"
	assert lines[1].rstrip() == "  spam here"
	assert lines[2].rstrip() == "    egg here"
	assert len(lines) == 3


def test_demo_logginghandler():
	import rrlog.server.filewriter
	ffs = OpenFF()
	print "open->%s"%(ffs)
	oldopen = rrlog.server.filewriter.open_
	rrlog.server.filewriter.open_ = ffs

	from demo import demo_logginghandler
	
	assert len(ffs.d) == 1
	# right file content ?
	def assert_(msgcount,lines,i):
		s = (
		"^\s*%d\.\[.+\]\s"%(i+1)
		+"A warning via standard logging #%s"%(msgcount)
		+regex_for_path("<module>", "demo_logginghandler", 69, "1,99", 1, omittedcxn="\<-\.\.\.<-")
		)
		rex = re.compile(s)
		line = lines[i]
		assert rex.match(line), "\n%s does not match:\n%s\nmsgcount was %d,index was %d"%(line,s,msgcount,i)
		
	ff = ffs.ff_by_suffix("-0.txt")
	
 	print "-----------------"
	for l in ff.lines:
		print l
	print "-----------------"
	
	assert len(ff.lines)==7
	assert_(0,ff.lines,0)
	assert_(6,ff.lines,6)
	rrlog.server.filewriter.open_ = oldopen
	
	

def test_demo_stdout():
	import rrlog.server.printwriter
	from rrlog.test.test_printwriter import FakeFile
	ff = FakeFile()
	rrlog.server.printwriter.print_ = ff.write
	
	from demo import demo_stdout

	print "--------------------------"
	for i,l in enumerate(ff.lines):
		print l
	print "--------------------------"
	
	for i,l in enumerate(ff.lines):
		assert l.rstrip()[l.index("Dear"):] == "Dear log reader, this is line #%s :::<module> |demo_stdout(48)"%(i)
	assert len(ff.lines) == 25
	


def test_demo_files():
	import rrlog.server.filewriter
	ffs = OpenFF()
	print "open->%s"%(ffs)
	oldopen = rrlog.server.filewriter.open_
	rrlog.server.filewriter.open_ = ffs

	from demo import demo_files
	assert len(ffs.d) == 3 # 3 files by rotation
	# right file content ?
	def assert_(msgcount,lines,i):
		# match the default line formatting:
		s = (
		"^[A-Z ] %d\.\[.+@.+\]\s"%(i+1)
		+r"This is log line #%d"%(msgcount)		
		+regex_for_path("<module>", "demo_files", 52, 1, 1)
		)
		rex = re.compile(s)
		line = lines[i]
		assert rex.match(line), "\n%s does not match:\n%s\nmsgcount was %d,index was %d"%(line,s,msgcount,i)
		
	ff = ffs.ff_by_suffix("-0.txt")
	assert len(ff.lines)==10
	assert_(0,ff.lines,0)
	assert_(9,ff.lines,9)
	ff = ffs.ff_by_suffix("-1.txt")
	assert len(ff.lines)==10
	assert_(10,ff.lines,0)
	ff = ffs.ff_by_suffix("-2.txt")
	assert len(ff.lines)==5
	assert_(24,ff.lines,4)
	
	rrlog.server.filewriter.open_ = oldopen


	
	
if __name__ == "__main__":
	import sys
	from rrlog.test import run
	#run(sys.argv[0],k="test_demo_indentf")
	run(sys.argv[0])
	