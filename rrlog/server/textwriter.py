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
Abstract base for text line logging.
@author: Ruben Reifenberg
"""

from rrlog.tool import tm_strftime
import time

def tm_structconverter(secs, to_structtime=time.localtime):
	"""
	:param secs: float, as returned by time.time()
	:returns: (struct_time,milliseconds)
	
		where struct_time is a tuple as returned by time.localtime,
		milliseconds is an int >=0 and <1000
	"""	
	msecs = long((secs%1)*1000) # no rounding, cut digits after 3rd:
	return to_structtime(secs),msecs


#todo: new:Formatter-objects. Configured datefmt missing here
class Formatter(object):
	"""
	This resembles the L{logging.__init__.Formatter} of the Python Logging Package
	by using the same __init__ arguments. That allows conveniently replacing a formatter
	object of "one world" (standard logging resp. rrlog) with a formatter of the "other world".
	"""
	def __init__(self, fmt=None, datefmt=None):
		"""
		Initialize the formatter with specified format strings.

		Initialize the formatter either with the specified format string, or a
		default as described above. Allow for specialized date formatting with
		the optional datefmt argument (if omitted, you get the ISO8601 format).
		"""
		if datefmt is None:
			datefmt = "%m/%d %H:%M:%S;%3N"
		if fmt:
			self._fmt = fmt
		else:
			self._fmt = "%(message)s"
		self.datefmt = datefmt
		
		
	def __call__(self, job, lineCount):
		"""
		:returns: formatting single-line string
		"""
		def cfunc():
			if job.cfunc is not "": return ":::%s"%(job.cfunc)
			else: return ""
		return "%1s %s.[%s:%s@%s] %s %s %s\n"%(
			job.cat,
			lineCount,
			job.pid,
	#		job.threadname, # laestig, aber aktivierbar
	#		job.tid,
			job.msgid,
			tm_strftime(self.datefmt,*tm_structconverter(job.ts)), #toopt: job could store (lazy created) msecs
			job.msg,
			#self.cfn_cln(job), # path-str includes the cfn/cln now
			cfunc(),
			job.pathStr(0),
			)

defaultFormatter = Formatter()



class TextlineLogWriter(object):
	"""
	Abstract base class for text line writers
	"""
	def __init__(self, format_line=None):
		"""
		:param format_line: Callable, takes a job and returns a single message line as str.
		
			See L{MsgJob} for job attributes available.
			See L{textwriter.Formatter.__call__} for an example.
		"""
		self._lineCount = 0
		if format_line is not None:
			self._format_line=(format_line,)
		else:
			self._format_line=(defaultFormatter,)


	def estimateLineCount(self):
		"""
		For performance reasons, it is allowed to estimate instead count exactly.
		(Intended for implementations which need to read access written data to count;
		but not required here, we are simply counting exactly.)
		
		:returns: count of already written log lines
		"""
		return self._lineCount


	def cfn_cln(self, job):
		"""
		Convenient string for callers file name / callers line number
		
		:rtype: str
		:returns: "\*<cfn>(<cln>)", "" if these data are not available (i.e. stack logging disabled)
		"""
		cln = job.cln()
		if cln != -1:
			return "*%s(%s)"%(job.cfn(),cln)
		else:
			return ""

