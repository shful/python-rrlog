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
rrlog - a Rotating Remote LOG.
@author: Ruben Reifenberg
"""

__version__="0.3.1"

import os
import sys
import time
import threading
import traceback
import warnings # Python 2.7 hides DeprecationWarning. Use python -Wd

from rrlog.tool import traceToShortStr
from rrlog import logging23

now = time.time


class SilentErrorHandler(object):
	"""
	Use this as errorHandler if you want log errors
	to disappear silently (e.g.in case of a Log Server Crash).
	Not recommended (but preferred over an exception
	in the log() call stopping the application).
	"""
	def handleException(self, e):
		pass


class StdoutErrorHandler(object):
	"""
	Use this as errorHandler if you want to see
	Errors (in case of a Log Server Crash)
	in standard out.
	This is not good in case of a CGI web app, because
	the printout may appear in the web page.
	"""
	def handleException(self, e):
		print("Logging Error: %s"%(e))
		print(traceToShortStr())


class StderrErrorHandler(object):
	"""
	Use this as errorHandler if you want to see
	Errors (in case of a Log Server Crash)
	in standard error out.
	"""
	def handleException(self, e):
		sys.stderr.write("Logging Error: %s\n"%(e))
		sys.stderr.write(traceToShortStr())



class Log(object):
	"""
	Instances of this are callable and represent the runtime interface for the application.
	@ivar stackMax: See L{__init__}, can be modified anytime.
	@ivar traceOffset: See L{__init__}, can be modified anytime.
	"""
	def __init__(self,
		server,
		traceOffset=0,
		msgCountLimit = 1000000, #exclusive! Highest number is 1 less
		stackMax=1,
		errorHandler=None,
		catsEnable=None,
		catsDisable=None,
		seFilesExclude=None,
		name=None,
		extractStack=True,
		):
		"""
		:param catsEnable:
			None or cat strings, e.g.("E","W","").						
			(Remember, the empty cat "" is the default.)
			If a list is specified, only these cats are logged, all other calls are ignored.
			If None, all cats are enabled.
		:type catsEnable: iterable of str
		
		:param catsDisable:
			All cats in this list are ignored.
			Default=None. Cannot be used along with catsEnable.
		:type catsDisable: iterable of str
					
		:param traceOffset:
			Adjusts the start point of the logged stack trace.
			
			Default == 0. Increase to 1 to hide the first call (e.g. if the log is called with a wrapper), and so on.
			Values too high are silently adjusted to the highest value possible.
		:type traceOffset: int
			 
		:param stackMax: 0==show no stacktrace,	1==log one stack line (the line where log(...) was called),
			2==log two stack lines, and so on.
			Default: 1 (==log callers line and nothing else.)
			See also: extractStack parameter.
		:type stackMax: int
			
		:param errorHandler:  Receives any Exception
			that occurs while logging.
			(e.g.a connection failure to the log server)
			If handler is None: No handling, your application
			will receive any exception occurring inside the log() call.
			For convenience, you may provide one of these strings:
			"stderr","stdout","silent" (case-insensitive).
			These strings are translated
			into the appropriate built-in "~ErrorHandler" class.
			
		:param seFilesExclude: filenames to exclude from Stack Extraction
			None (==nothing to exclude), or a callable that returns True/False when given a filename.
			When True, the file does NOT appear in the call path.
			None is acepted instead of False too, just to enable pragmatic ideas like
			seFilesExclude=re.compile("foo/bar.*").search
			(which exludes all foo/bar* files).
			Note: The first path element (callers file name - cfn) is never excluded this way. Only the rest of the trace may be "censored".
			
		:param name: defaults to class name. For individual use (to identify the log object). The log itself does not evaluate it but use it with its __repr__/__str__ method.
		:type name: str
		
		:param extractStack: If False, stack extraction is disabled. This improves performance (can be more than twice), but any stack related functionality will not work (e.g.line indention to visualize call hierarchy).
		:type extractStack: bool
			
		"""
		assert (catsEnable is None) or (catsDisable is None), "Can't use both catsEnable and catsDisable same time"
		if catsEnable is not None:
			assert hasattr(catsEnable,"__iter__") and (not isinstance(catsEnable,str)),"catsEnable must be None or list of str"
		if catsDisable is not None:
			assert hasattr(catsDisable,"__iter__") and (not isinstance(catsDisable,str)),"catsDisable must be None or list of str"

		if name is None:
			name = self.__class__.__name__
			
		self._on = True
		
		self._msgCount = 0
		self.traceOffset = traceOffset
		self._server = server
		self._server.addClient()
		self.msgCountLimit = msgCountLimit
		self.stackMax = stackMax
		if str(errorHandler).lower()=="stderr": errorHandler=StderrErrorHandler()
		elif str(errorHandler).lower()=="stdout": errorHandler=StdoutErrorHandler()
		elif str(errorHandler).lower()=="silent": errorHandler=SilentErrorHandler()
		elif isinstance(errorHandler,str): raise TypeError("probably mistyped str value for errorHandler:%s"%(errorHandler))
		self._errorHandler = errorHandler
		self.catsEnable = catsEnable
		self.catsDisable = catsDisable
		self._seFilesExclude = seFilesExclude
		self.name = name
		self._extractStack = extractStack
		self._sticked_items = {}


	def logging23_handler(self):
		"""
		Note that, contrary to the Python logging, the rrlog is not designed/tested for threading.
		
		:returns: Handler for the Python >=2.3 standard logging framework.
		"""
		return logging23.handler(self)


	def _getCallPath(self,tb,depth):
		"""
		:returns: path,cfuncname where path = ( (filename,lineno), ...), len >=0
			cfuncname is "" if no traceback available, 
			None if no cfuncname exists (log call at module level)
			
		:param depth: log-internal call depth when the traceback was taken.
		:type depth: int
			
		"""
		if len(tb) == 0:
			return (),"" # return ((None,-1),),None
		
#		tb = traceback.extract_stack(limit=self._extract_stack_limit(depth)) #limit >=0, 0==no lines etc.
		calldepth = -1-depth # -1 is current. Ignore current and all previous log-internal calls.
		
		try:
			line = tb[calldepth]
		except IndexError:
			# This happens - in the following case:
			# Log is created with traceOffset == 1
			# because a module uses a log() function for later log() calls.
			# But creation itself is in a place not deep enough
			# and logging of this Log creation may fail here.
			calldepth += 1
			try:
				line = tb[calldepth]
			except IndexError:
				# impossible depth was given: sadly, we should not fail here :-(
				# Legal Scenario: traceOffset is given a high value to adjust for standard logging
				# another Python version theoretically can refactor the logging framework to have shorter tracebacks
				# And the application still should not fail because of that.
				calldepth = len(tb)-1
				line = tb[calldepth]
		depth = calldepth # - 1 # -1, um line nicht nochmal zu sehen

		path = []
		cfuncname = None
		stackRest = self.stackMax
		
		while stackRest > 0:
			try:
				line = tb[depth]
			except IndexError: break
			else:
				if (self._seFilesExclude is None)\
 					or not (self._seFilesExclude(line[0])):
					stackRest -= 1
					path.append( (line[0],line[1]) )
					if cfuncname is None:
						cfuncname = line[2] # special treatment: don't add it to every path item, we want it for the first only
				else:
					# add a "None" line indicating an item is omitted
					path.append( (None,None) )
			depth -= 1
			
		return path,cfuncname


	def _createServerData(self,tb,depth,message,cat,special):
		"""
		:returns: Tuple for the log server
		:param depth: log-internal call depth when the traceback was taken.
		:type depth: int
		"""
		self._msgCount += 1
		
		if self._msgCount == self.msgCountLimit:
			self._msgCount = 1
			
		try:
			ospid = os.getpid() # need to get it always. When saving it, a process could fork me after that.
		except Exception as e:
			import warnings
			warnings.warn("log: could not obtain process id from your operating system. You'll see -1 there.")
			ospid = -1

		path,cfuncname = self._getCallPath(tb,depth)
		t = threading.currentThread()
		
		try:
			tid = t.ident # >= python 2.6 only
		except AttributeError:
			tid = None
			
		return (
			self._msgCount,
			ospid,
			tid,
			t.name,
			now(),
			message,
			cat,
			path,
			len(tb),
			cfuncname,
			special,
			)


	def on(self):
		self._on = True
		
		
	def off(self):		
		self._on = False


	def set_sticked_items(self, asdict):
		"""
		Tip: To obtain the Log instance while using standard logging module,
		take it from the Logger.handlers list.
		
		:param asdict: key/value pairs, that this Log object will append to every succeeding log call.
			Similar to the "special" dict but sticky.
			Previous "sticked data" are replaced.
		
			Example: {"ip":requests_ip_address}
			
			Call with {} to end sticking data.
		"""
		assert hasattr(asdict,"__getitem__"), "need dictlike object, got %s"%(type(asdict))
		self._sticked_items = asdict
		

	def __call__(self, message, cat="", special=None, traceDepth=1, **kwargs):
		"""
		:param message: String to be logged
		:param cat: application specific category, e.g. "E"=Error,"W"=Warning. Default is "".
			
		:param special: dict-like object (only the items() -> (k,v)-iter method is required)
				The items of the "special" dict appear in the Jobs at the server side. Custom observers,
				filters, writers and formatters can use these.
				
				Type restrictions: only {str: str|int} is allowed for the dict items (!)
		:type special: {str: str|int} or None
				
		:param traceDepth: Adjusts the starting point of stacktrace logging.
				Default=1. Typically, you may increase that if you call the log with a wrapping function which should be hidden in the stacktrace.
				This adjusts the current call only. See traceOffset in L{__init__} for a permanent adjustment.
				
		:param Kwargs:
			**Deprecated**  Use the "special" dict only.
			You can provide any custom kwargs you like. This is sugar for convenience,
			all kwargs are put into the "special" dict.
			kwargs items override both items of special dict and sticked items silently.
			
		:returns: log-client specific message number,starting with 1 (not unique at server side, if multiple log clients are used.) 
		"""
		if (self.catsEnable is not None) and (cat not in self.catsEnable):
			return
		elif (self.catsDisable is not None) and (cat in self.catsDisable):
			return
		
		if not self._on:
			return

		if self._sticked_items:
			# add these items into special
			if special is None: special = kwargs
			else: special.update(kwargs)
			
		if kwargs:
			warnings.warn("custom kwargs in the log call are deprecated. Use the 'special (dict)' parameter", DeprecationWarning)
			# add these items into special
			if special is None:
				special = kwargs
			else:
				special.update(kwargs)
		
		if self._extractStack:
			tb = traceback.extract_stack()
		else:
			tb = ()
		sd = self._createServerData(
			tb,
			traceDepth+self.traceOffset,
			message,
			cat,
			special,
			)
		
		try:
			self._server.log(sd)
		except Exception as e:
			if self._errorHandler is not None:
				self._errorHandler.handleException(e)
			else:
				raise # Exception(str(e)+traceToShortStr())
		else:
			return sd[0]


	def __repr__(self):
		def on():
			return {True:"on",False:"Off"}[self._on]
		
		return "%s(%s)"%(self.name,on())
