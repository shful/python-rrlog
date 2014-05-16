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








from rrlog.server.filewriter import createLocalLog

# This uses a custom line formatting
def format_line(job, lineCount):
	# A named argument ("ip") was added ad hoc in the log calls. It's available here the formatting method:
	return "Original message = '%s'. And the ip address is:%d\n"%(job.msg, job.special.get("ip",-1)) # default -1 when ip is missing

log = createLocalLog(
   	format_line=format_line,
	filePathPattern="./demo-log-%s.txt", # "pattern" because %s (or %d) is required for the rotate-number
	rotateCount=3, # rotate over 3 files
	rotateLineMin=10, #at least 10 lines in each file before rotating
	)

# now, log some lines:
for i in xrange(25):
	log("customized-line %s"%(i), special={"ip":12345} )
log("customized-line without ip")
