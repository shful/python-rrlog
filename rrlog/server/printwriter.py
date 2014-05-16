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
Log to stdout.
@author: Ruben Reifenberg
"""

import sys

from rrlog import Log
from rrlog import server
from rrlog.server import textwriter

print_ = sys.stdout.write # tests replace print_


def createServer(writer=None, tsFormat=None, filters=None, observers=None, writeMsgid=False, format_line=None):
	"""
	:param tsFormat: timestamp format. See L{rrlog.server.LogServer.__init__}
	:param filters: default = () See L{rrlog.server.LogServer.__init__}
	:param observers: default = () See L{rrlog.server.LogServer.__init__}
	:param format_line: See L{rrlog.server.textwriter.TextlineLogWriter.__init__}
	"""
	if writer is None:
		writer = LOGWRITER_CLASS(
		 	writeMsgid=writeMsgid,
		 	format_line=format_line,
		)
	
	return server.LogServer(
		writer = writer,
		filters = filters,
		observers = observers,
		tsFormat = tsFormat,
		)

def createLocalLog(
	writer=None,
	filters=None,
	observers=None,
	traceOffset=0,
	tsFormat=None,
	writeMsgid=False,
	stackMax=1,
	catsEnable=None,
	catsDisable=None,
	seFilesExclude=None,
	format_line=None,
	name=None,
	extractStack=True,
	):
	"""
	:param catsEnable: see L{rrlog.Log.__init__}
	:param catsDisable: see L{rrlog.Log.__init__}
	:param seFilesExclude: see L{rrlog.Log.__init__}
	:param filters: see L{rrlog.server.LogServer.__init__}
	:param observers: see L{rrlog.server.LogServer.__init__}
	:param tsFormat: timestamp format. See L{rrlog.server.LogServer.__init__}
	
		Here, the default is None (shows no time stamps)
		
	:param stackMax: see L{rrlog.Log.__init__}, default: 5 (==log 5 stack levels.)
	:param format_line: See L{rrlog.server.textwriter.TextlineLogWriter.__init__}
	:param name: The log can be identified by its optional name attribute (__repr__ method of the log will use it.)
	:param extractStack: see L{rrlog.Log.__init__}
	
	:returns: a Log ready to use
	"""
	if writer is None:
		writer = LOGWRITER_CLASS(
		 	writeMsgid=writeMsgid,
		 	format_line=format_line,
		)
		
	return Log(
		server = createServer(
		  	writer=writer,
			tsFormat=tsFormat,
			filters=filters,
			observers=observers,
			),
		traceOffset=traceOffset,
		stackMax=stackMax,
		catsEnable=catsEnable,
		catsDisable=catsDisable,
		seFilesExclude=seFilesExclude,
		name=name,
		extractStack=extractStack,
		)




class PrintLogWriter(textwriter.TextlineLogWriter):
	"""
	"""
	def __init__(self, writeMsgid=False, format_line=None):
		textwriter.TextlineLogWriter.__init__(self, format_line)
		self.writeMsgid = writeMsgid

	def _format_line(self, job):
		"""
		Default formatting method.
		
		:rtype: str
		:returns: single log line
		"""
		def pre():
			if self.writeMsgid: return "[%s]"%(job.msgid)
			else: return ""
			
		return "%s%s %s %s %s\n"%(
			pre(),
			job.msg,
			self.cfn_cln(job),
			job.pathStr(1),
			job.ts,
			)
		
		
	def close(self):
		pass


	def writeNow(self, job):
		"""
		Write without buffering, return when written
		"""
		print_(
			self._format_line[0](job,lineCount="")
			) #todo:lineCount="" is a hack (for empty output without linecount)


LOGWRITER_CLASS = PrintLogWriter
