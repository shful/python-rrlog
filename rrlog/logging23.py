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
@summary: Integration into Python 2.3 logging as a Handler
@author: Ruben Reifenberg
@var LEVELMAP: 1:1 mapping of single characters (Like "E") to the level constants of the standard logging module;
{logging-level: Category-Character}. You may modify this.
"""



from logging import Handler,CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET


LEVELMAP = {
	CRITICAL: "C", # == FATAL
	ERROR: "E",
	WARNING: "W",
	INFO: "I",
	DEBUG: "D",
	NOTSET: "",
	}


def seFilesExclude(fname):
	"""
	callable that exludes logging.__init__ from stack extraction.
	:returns: True if fname is "logging/__init__.py"
	"""
	return fname.endswith("logging/__init__.py")


class _Handler(Handler):
	def __init__(self, log, level=NOTSET):
		"""
		:param log: Your ready-to-use log object
		:param level: One of the ordered standard logging constants (INFO, ERROR etc.)
		"""
		Handler.__init__(self, level)
		self._log = log

	def emit(self, record):
		self._log(
			record.getMessage(),
			cat=LEVELMAP.get(
				record.levelno,
				"",
				),
			traceDepth=2,
			)
		

def handler(*args, **kwargs):
	return _Handler(*args, **kwargs)


def useALogger():
	logger = logging.getLogger("gimmeALogger")
	for i in range(0,7):
		logger.info("info%d?"%(i))
		logger.warn("warning%d?"%(i))
		logger.error("error%d?"%(i))
		

if __name__ == "__main__":
	from rrlog.server.filewriter import createLocalLog # local == all in same process, no separate server
	log = createLocalLog(
			filePathPattern="./integrated-log-%s.txt", # "pattern" because %s (or %d) is required for the rotate-number
			rotateCount=3, # rotate over 3 files
			rotateLineMin=10, #at least 10 lines in each file before rotating
			#seFilesExclude=seFilesExclude,
			)
	import logging
	logger = logging.getLogger("gimmeALogger")
	logger.setLevel(WARNING)
	logger.addHandler(handler(log))
	useALogger()
