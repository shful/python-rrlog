
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
Tests can be run with py.test (of the PyPy project)
or with nosetest either.
nosetest is default with v0.2.0 because PY3k compliance is expected earlier here.
@author: Ruben Reifenberg
"""
def run_nose(srcfile,k=None):
	import os,sys
	cmd  = "nosetests"
	if k is not None:
		k = k+".*" # nose takes a regex pattern
		cmd += " -m %s"%(k)
	cmd += " %s"%(srcfile)
	os.system(cmd)

def run_pytest(srcfile, k):
	import py
	args = py.std.sys.argv[1:]
	if k is not None:
		args += ["-k",k]
	py.test.cmdline.main(args+["-s","-x",srcfile])
	#os.system("py.test %s -s -x "%(srcfile) # required when running >1 test in same process


def run(srcfile, k=None):
	"""
	:param srcfile: str, filename to test, e.g. sys.argv[0]
	:param k: str, run tests starting with regex k.* only. ==The -k parameter of py.test.
	"""
	#run_nose(srcfile, k)
	run_pytest(srcfile, k)

if __name__ == "__main__":
	import os
	for (dirpath,dirnames,filenames) in os.walk("./"):
		for filename in filter(lambda x:x.startswith("test") and x.endswith(".py"), filenames):
			print "::::::: CALLING test of file %s :::::::"%(filename)
			run(filename)
