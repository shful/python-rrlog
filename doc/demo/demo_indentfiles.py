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
from rrlog.contrib import stackindent

# add a filter while log creation:
log = filewriter.createLocalLog(
	filePathPattern="./demo-log-%s.txt",
	tsFormat=None, # no time stamps
	rotateCount=1,
	rotateLineMin=None, # no rotation
	filters=(stackindent.StackIndentFilter(token="--"),), # indent with one "--" per stack level
	)

# log as usual. The first call will "tara" the indention to zero.
def egg():
	log("egg here")

def spam():
	log("spam here")
	#log("did tara=0",stackindent_tara=0) # tara would adjust the indent to 0
	egg()

log("begin")
spam()