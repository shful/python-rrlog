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
logging into text files.
@author: Ruben Reifenberg
"""

import os.path
import thread
import warnings
from rrlog import Log
from rrlog import server
from rrlog.server import textwriter


open_ = open

def createRotatingServer(
	filePathPattern, 
	rotateCount,
	rotateLineMin,
	tsFormat="std1",
	filters=None,
	observers=None,
	logwriterFactory=None,
	drop=True,
	format_line=None,
	fileClosed=None
	):
	"""
	:param filePathPattern: full log filename incl.path and placeholder for an int (rotate number). E.g."./mylog%d.txt"
	:param tsFormat: timestamp format. See L{rrlog.server.LogServer.__init__}
	:param rotateCount: int >>1, how many files to use for rotation
	:param rotateLineMin: rotate when ~ lines are written. None to switch off rotation.
	:param filters: default = () See L{rrlog.server.LogServer.__init__}
	:param observers: default = () See L{rrlog.server.LogServer.__init__}
	:param logwriterFactory: Creates LogWriter instances (one per file). If None, the module variable LOGWRITER_CLASS is used.
	:param format_line: See L{rrlog.server.textwriter.TextlineLogWriter.__init__}
	:param fileClosed: Experimental, undocumented. Use case: Zip a log file after rotation. Parameter May change.
	"""
	if logwriterFactory is None:
		logwriterFactory = lambda *args,**kwargs:LOGWRITER_CLASS(
			format_line=format_line,
			fileClosed=fileClosed,
			*args,
			**kwargs
			)		
	elif format_line is not None:
		warnings.warn("format_line is ignored because logwriterFactory is already specified")
		
	return server.LogServer(
		writer = server.RotateLogWriter(
			getNextWriter = server.RotateWriterFactory(
				configs=[FileConfig(
					filepath=filePathPattern%(i),
					drop=drop,
					)
					for i in range(0,rotateCount)
					],
				writerFactory=logwriterFactory,
				).nextWriter,
			rotateLineMin=rotateLineMin,
			),
		filters = filters,
		observers = observers,
		tsFormat = tsFormat,
		)


def createLocalLog(
	filePathPattern,
	rotateCount,
	rotateLineMin,
	filters=None,
	observers=None,
	traceOffset=0,
	tsFormat="std1",
	stackMax=5,
	drop=True,
	catsEnable=None,
	catsDisable=None,
	seFilesExclude=None,
	format_line=None,
	name=None,
	extractStack=True,
	fileClosed=None,
	):
	"""
	:param catsEnable: see L{rrlog.Log.__init__}
	:param catsDisable: see L{rrlog.Log.__init__}
	:param seFilesExclude: see L{rrlog.Log.__init__}
	:param filters: see L{rrlog.server.LogServer.__init__}
	:param observers: see L{rrlog.server.LogServer.__init__}
	:param tsFormat: timestamp format. See L{rrlog.server.LogServer.__init__}
	:param filePathPattern: full log filename incl.path and placeholder for an int (rotate number). E.g."./mylog%d.txt"
	:param rotateCount: int >>1, how many files to use for rotation
	:param rotateLineMin: rotate when ~ lines are written. None to switch off rotation.
	:param stackMax: see L{rrlog.Log.__init__}, default: 5 (==log 5 stack levels.)
	:param drop: if True, drop an eventually existing file. When False, append to an existing one (this is possible with rotateCount==1 only).
	:param format_line: See L{rrlog.server.textwriter.TextlineLogWriter.__init__}
	:param name: The log can be identified by its optional name attribute (__repr__ method of the log will use it.)
	:param extractStack: see L{rrlog.Log.__init__}
	:param fileClosed: Experimental, undocumented. Use case: Zip a log file after rotation. Parameter May change.
	:returns: a Log ready to use
	"""
	try:
		filePathPattern%77
	except TypeError:
		raise ValueError("filePathPattern (%s) needs a placeholder for the rotate number"%(filePathPattern))
	
	return Log(
		server = createRotatingServer(
			filePathPattern,
			rotateCount,
			rotateLineMin,
			tsFormat=tsFormat,
			filters=filters,
			observers=observers,
			drop=drop,
			format_line=format_line,
			fileClosed=fileClosed,
			),
		traceOffset=traceOffset,
		stackMax=stackMax,
		catsEnable=catsEnable,
		catsDisable=catsDisable,
		seFilesExclude=seFilesExclude,
		name=name,
		extractStack=extractStack,
		)


class FileClosedEvent(object):
	"""
	The specified log file was closed.
	"""
	def __init__(self, filePath, lineCount):
		"""
		:param filePath: full log filename incl.path
		:param lineCount: line count of the closed file
		"""
		self.filePath = filePath
		self.lineCount = lineCount


class FileConfig(object):
	"""
	Describes a single log file.
	I.e.for log rotation, a sequence of this is required.
	"""
	def __init__(self,
		filepath,
		drop=True,
		lazy = True,
		):
		"""
		:param drop: False: Append lines to existing log file (This makes no sense when using file rotation.)
				True: A new Writer clears the existing logfile.
		:param filepath: full log filename incl.path
		:param lazy: If True, file is opened with first log entry (default)
				If False, file is opened immediately.
				Use False only if you know hat you're doing.
				With socket server, it may result in data loss: the first file is opened immediately
				before the worker thread starts.
				Then, the worker thread uses the already opened file which fails.
				(Another solution for that case might be always close/re-open the file fo reach written line.)
		"""
		self.filepath = filepath
		self.lazy = lazy
		
		if drop:
			self.fileopenflag="w"
		else:
			self.fileopenflag="a"

			
	def __repr__(self):
		return "%s[%s]"%(self.__class__.__name__,self.filepath)


class FileLogWriter(textwriter.TextlineLogWriter):
	"""
	"""
	def __init__(self, config, format_line=None, fileClosed=None):
		"""
		:param config: FileConfig
		"""
		textwriter.TextlineLogWriter.__init__(self, format_line=format_line)
		
		self._fileClosed = fileClosed
		self._config = config
		
		if not config.lazy:
			self._createFile()
		else:
			self._logfile = None


	def _createFile(self):
		self._logfile = open_(
			self._config.filepath,
			self._config.fileopenflag
			)  # not file(). open seems to be kept with Py3k
		
		
	def close(self):
		self._logfile.close()
		if self._fileClosed:
			self._fileClosed(
				FileClosedEvent(
					self._config.filepath,
					self._lineCount
					)
				)


	def writeNow(self, job):
		"""
		Write without buffering, return when written.
		Flushes the file after each write.
		"""
		if self._logfile is None:
			# filelazy was set, and this is the first log message: open file
			self._createFile()
			
		self._lineCount += 1

		#todo: encode("utf-8") is rubbish
		#lets specify unicode logging, and use codes.open with utf-8 or custom encoding
		self._logfile.write(
			self._format_line[0](
				job,
				self._lineCount
				).encode("utf-8")
			)
		self._logfile.flush()

		
	def __str__(self):
		def fname():
			if self._logfile:
				miss={True:"",False:"miss!"}[os.path.exists(self._logfile.name)]
				if self._logfile.closed:
					return "(closed)"+miss+self._logfile.name
				else:
					return "(open)"+miss+self._logfile.name
			else:
				return "no file"
			
		return u"{}-{}-{}".format(
			self.__class__.__name__,
			fname(),
			thread.get_ident()
			).encode("ascii","backslashreplace")

	
	def __repr__(self):
		return self.__str__()


LOGWRITER_CLASS = FileLogWriter
