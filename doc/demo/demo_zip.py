#!/usr/bin/env python


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
Pending feature "logfile zipping" is undocumented.
@author: Ruben Reifenberg
"""








from rrlog.server import filewriter

import zipfile
import warnings

# new with v0.3.1: zip a logfile. Experimental feature, undocumented !
def zip(ev):
	try:
		f = zipfile.ZipFile(ev.filePath+".zip","w")
		f.write(ev.filePath)
		f.close()
	except IOError,e:
		warnings.warn("zipping %s failed: %s".format(ev.filePath, e))

log = filewriter.createLocalLog(
		filePathPattern="./demo-zip-%s.log", # "pattern" because %s (or %d) is the rotation index
		rotateCount=3, # rotate over 3 files
		rotateLineMin=10, #at least 10 lines in each file before rotating
		fileClosed=zip,
		)

# now, log some lines:
for i in xrange(25):
	log("line #%s"%(i))
