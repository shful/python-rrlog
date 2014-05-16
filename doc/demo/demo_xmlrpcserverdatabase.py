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








# First, create a pure database-writing server:
# (this is independent from the connection type, like XMLRPC)
from rrlog.server import dbwriter_sa
engineStr = "mysql://logtester@localhost/logtest"

logServer = dbwriter_sa.createRotatingServer(
	engineStr = engineStr,
	tableNamePattern = "logtable_%s",  # "pattern" because %s (or %d) is required for the rotate-number
	rotateCount=3,
	rotateLineMin=10,
    tsFormat="std1", # Timestamp format: std1 is shorthand for the strftime-format "%H:%M.%S;%3N"
	)

# Start the server as an XMLRPC server:
from rrlog.server import xmlrpc

xmlrpc.startServer(
	logServer,
	ports=(9804,9805,9806,), # try in this order, use the first port available
	)
# The server waits for requests now.

