#!/usr/bin/env python


# Copyright (c) 2007 Ruben Reifenberg
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.






"""
@summary:
Demonstrates the basic usage.
@author: Ruben Reifenberg
"""








from rrlog.server import filewriter
from rrlog.logging23 import seFilesExclude

# Note: the OPTIONAL traceOffset skips the standard-logging-code from logged stacktraces
# Required value may depend on Python version! If given, seFilesExcluded is redundant. See Manual.
log = filewriter.createLocalLog(
		filePathPattern="./demo-log-%s.txt", # "pattern" because %s (or %d) is required for the rotate-number
		rotateCount=3, # rotate over 3 files
		rotateLineMin=10, #at least 10 lines in each file before rotating
		seFilesExclude=seFilesExclude, # optional, remove all "logging.__init__" from logged stack path
#		traceOffset=5, # optional, value fits with Python2.5
		stackMax=20,
		)





import logging

logger = logging.getLogger("Demo")
logger.setLevel(logging.WARNING)
logger.addHandler(log.logging23_handler())

# standard logging calls should work now:
for i in xrange(7):
	logger.info("An info via standard logging #%s"%(i)) # omitted !
	logger.warn("A warning via standard logging #%s"%(i))
