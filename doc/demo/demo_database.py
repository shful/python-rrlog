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








from rrlog.server import dbwriter_sa

# This is a RFC-1738 style URL, as required by SQLAlchemy.
# It includes in this order:
# the database type (e.g.mysql,postgres,sqlite...)
# the database user (that has write permission)
# the database name (here: "logtest")
# See SQLAlchemy Doc for a more accurate and up-to-date description.
engineStr = "mysql://logtester@localhost/logtest"

log = dbwriter_sa.createLocalLog(
	engineStr = engineStr,
	tableNamePattern = "logtable_%s",  # "pattern" because %s (or %d) is required for the rotate-number
	rotateCount = 3, # rotate over 3 tables
	rotateLineMin = 10, # at least 10 lines in each table before rotating
	)

# log 31 lines rotating -> first table has exactly one message (the last)  
for i in xrange(31):
	log("usingDatabase: this is line #%s"%(i))
