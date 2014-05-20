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
Log Server,
Part of the log which can (optionally) be in a separate process.
@author: Ruben Reifenberg
"""

from sys import stderr
from datetime import datetime
from rrlog.tool import mStrftime,ListRotator,traceToShortStr
from rrlog.globalconst import warn
import collections

EMPTYDICT = {}


class ColumnConfigurationMismatch(Exception):
	"""
	A configured column name is impossible because already reserved.
	"""
	pass


class ObserverAlreadyAdded(Exception):
	"""
	Attempt to add an observer twice into the observer list
	"""
	pass


class MsgJob(object):
	"""
	@ivar threadname: part of client identification
	@ivar msgid: int, id of the message. Unique in the client.
	@ivar msg: str, msg as created by the client.
	@ivar ts: str, timestamp
	@ivar special: dict with custom items (see "special" argument of the log method)
	@ivar tblen: len of the client traceback when the log method was called
	@ivar path: client traceback path as sequence of (filename, linenumber). [0] is the latest (where the log call happened)
	"""
	#			msgid, pid, tid, threadname, ts, msg, cat, path, tblen, cfunc, special):
	def __init__(self,msgid, pid, tid, threadname,ts,msg,cat,path,tblen,cfunc,special,formatter):
		"""
		:param special: data for custom observers only
		:param ts (str): timestamp
		"""
		self.pid = pid
		self.tid = tid
		self.threadname = threadname
		self.msgid = msgid
		self.msg = msg
		self.ts = ts
		if special is None: self.special = EMPTYDICT
		else: self.special = special
		self.cat = cat
		self.path = path
		self.tblen = tblen
		self._formatter = formatter
		self.cfunc = cfunc
		self._iCfn = None # index of cfn in path (first non-None element)
		
		for i,(cfn,cln) in enumerate(path):
			if cfn is not None:
				self._iCfn = i
				break


	def cfn(self):
		"""
		:rtype: str
		:returns: Callers File Name
		"""
		if self._iCfn is not None:
			return self._formatter.format_fname(self.path[self._iCfn][0])
		else:
			return None
		

	def cln(self):
		"""
		:rtype: int
		:returns: Callers Line Number
		"""
		if self._iCfn is not None:
			return self.path[self._iCfn][1]
		else:
			return -1


	def getFormattedDict(self):
		"""
		DEPRECATED: use format_dict of the DBLogWriter
		:rtype: dict
		:returns: already formatted data
		"""
		import warnings
		warnings.warn("use format_dict argument of DBLogWriter.__init__",DeprecationWarning)
		# self.__dict__ wouldn't have the formatted stuff like cfn
		res = dict(
			pid=self.pid,
			threadname = self.threadname,
			msgid = self.msgid,
			msg = self.msg,
			cat = self.cat,
			ts = self.ts,
			cfunc=self.cfunc,
			cfn = self.cfn(),
			cln = self.cln(),
			path = self.pathStr(0), # 0 since v0.1.5. Was 1 with <=v0.1.4 to omit the cfn/cln in the path string.
			)
		res.update(self.special)
		
		return res


	def pathStr(self, imin=0):
		"""
		:param imin: min.index of path to use.
		
			Fo example, imin==1 will skip the first path item
			(Note: the first item is also available separately as cfn,cln)
			
		:rtype: str
		:returns: path as formatted str
		"""
		return self._formatter.pathAsStr(self.path, imin=imin)


	def copy_update(self, kwargs):
		"""
		:returns: new instance with my init kwargs but updated with the given kwargs
		"""
		oldkwargs = {
			"pid":self.pid,
			"threadname":self.threadname,
			"msgid":self.msgid,
			"msg":self.msg,
			"ts":self.ts,
			"special":self.special,
			"cat":self.cat,
			"path":self.path,
			"tblen":self.tblen,
			"cfunc":self.cfunc,
			"formatter":self._formatter,
			}
		oldkwargs.update(kwargs)
		
		return self.__class__(**oldkwargs)

	
	def __str__(self):
		return "{}-{}-{}".format(
			self.__class__.__name__,
			self.cat,
			self.msg[:18],
			).encode("ascii","backslashreplace")

			
	def __repr__(self):
		return self.__str__()
	


class RotateWriterFactory(object):
	
	def __init__(self, configs, writerFactory):
		assert len(configs)>0
		self._configs = ListRotator(configs)
		self._writerFactory = writerFactory
		
	def nextWriter(self, history):
		"""
		Was RENAMED from next(), otherwise Python3 conversion failure.
		:param history: list of old writers to be maintained, oldest at [0]
		
			Invalid (expired) writers are removed!
		"""
		if len(history) >= self._configs.len():
			history.pop(0)
		
		return self._writerFactory(
			self._configs.__next__()
			)


class RotateLogWriter(object):
	"""
	Assigned to a list of LogWriters,
	rotates by creating a new one each time
	when a line count is exceeded.
	Maintains a history of old writers.
	@ivar writers: History of writers, current at [-1], oldest at [0].
	Only writers with an existing (i.e.not already overwritten) table/file are available.
	(Migration note: This is analogous to the getWriteHistory() of version 0.1.1 but the order is ascending.)
	"""
	def __init__(self, getNextWriter, rotateLineMin):
		"""
		:param getNextWriter: Callable that takes a list (history) of previous writers, and returns the next logWriter to use
		:param rotateLineMin: rotate when ~ lines are written
		"""
		self._rotateLineMin = rotateLineMin
		self._nextWriter = getNextWriter,
		self.writers = []
		self._rotate()


	def _rotate(self):
		"""
		Not threadsafe.
		Maintains the history (self.writers).
		A new writer is appended..
		removes the oldest writer [0] if self._writer count is longer than self._configs.
		"""
		writer = self._nextWriter[0](history=self.writers)
		if self.writers:
			self.writers[-1].close()
		self.writers.append(writer)


	def writeNow(self, logrecord):
		"""
		Write without buffering, return when written
		"""
		if (self._rotateLineMin is not None) \
			and (self.writers[-1].estimateLineCount() >= self._rotateLineMin):
			self._rotate()

		self.writers[-1].writeNow(logrecord)


class LogServer(object):
	"""
	This can (but must not be) in the application process.
	@cvar CAT_INTERNALERROR: Default "I". This is used as "cat" when I write a log message about a logging failure (if possible)
	"""
	CFN_SHORT = 1 # Caller File Names Minimal-Length
	CFN_FULL = 2 # Caller File Names with Full path
	CAT_INTERNALERROR = "I"

	def __init__(self,
		writer,
		filters = None,
		observers = None,
		cfnMode=1,
		tsFormat=None,
		jobhistSize=100,
		):
		"""
		:param cfnMode: One of the MODE...constants.
		
			CFN_SHORT: Caller File Names minimal,i.e.file name without directory path(=Default)
			CFN_FULL: Caller File Names with full file path)
			Default is CFN_SHORT
			
		:param tsFormat: strftime-format string with an extension: use %3N for milliseconds.
		
			[Year..second are: %Y/%y,%m,%d,%H,%M,%S]
			None for no timestamps.
			Standard Values for convenience:
			The String "std1" is interpreted as "%H:%M.%S;%3N", e.g. 13:59.59;999
			The String "std2" is interpreted as "%m/%d %H:%M.%S"
			
		:param observers: list of callables, called with args: jobhist, writer.
		
			Called each time after(!) a message was written.
			writer is the specific writer (depends on DB/file/Stdout modus.)		
			jobhist are the N last message-jobs, with the latests at [-1]. The size N of the jobhist
			is limited by jobhistSize. Increase jobhistSize if your observer needs to see a large job history.
			The observers are processed in the given order.
			You can modify job content for following observers, without affecting the log (since the observers are called after
			the line is written.)
			For compatibility: An observer can also have an observe() method. If available, this is used (instead of __call__)
			
		:param filters: list of callable objects, analogous to observers.
		
			But filters are called before logging. When they modify the message, the change gets visible in the log.
			
		:param jobhistSize: The count of recent messages that are available as a list (these may be read by observers). Default=100
		
		:raises AssertionError: if an observer is >1 times in the list
		:raises AssertionError: if a filter is >1 times in the list
		"""
		if filters is None:
			filters=[]
		else:
			assert hasattr(filters,"__iter__"),"filters must be a sequence, not %s"%(type(filters))
			filters = list(filters) # need the count method

		if observers is None:
			observers=[]
		else:
			assert hasattr(observers,"__iter__"),"observers must be a sequence, not %s"%(type(observers))
			observers = list(observers) # need count method and eventually want to append


		# BEGIN compatibility with v <= 0.1.4: Accept observers with observe() instead __call__(), too:
		self._observers = []		
		for i,x in enumerate(observers):
			if hasattr(x,"observe") and isinstance(x.observe, collections.Callable):
				self._observers.append(x.observe)
			else:
				assert isinstance(x, collections.Callable),"Observer %s must be callable (or need to have the deprecated observe() method)."%(x)
				self._observers.append(x)
		# END compatibility with v <= 0.1.4

		for x in observers:
			assert observers.count(x)==1, "%s is >1 times in observers list"%(x)

		for i,x in enumerate(filters):
			assert isinstance(x, collections.Callable),"Filter %s must be callable."%(x)
			assert filters.count(x)==1, "%s is >1 times in filters list"%(x)


		#self._time0 = datetime.now()
		self._observers = list(self._observers) # allow to append
		self._filters = filters
		self._tsFormat = {
			"std1": "%H:%M.%S;%3N",
			"std2": "%m/%d %H:%M.%S",
			}.get(tsFormat, tsFormat)
		self._cfnMode = cfnMode
		self._writer = writer
		self._jobhist = []
		assert jobhistSize>0, "need at least a history size of 1, not %s"%(jobhistSize)
		self._jobhistSize = jobhistSize


	def addObserver(self, observer):
		"""
		appends the observer at the end of the observers list
		"""
		if observer in self._observers:
			raise ObserverAlreadyAdded("already added: %s"%(observer))
		
		if hasattr(observer,"observe") and isinstance(observer.observe, collections.Callable):
			self._observers.append(observer.observe)
		else:
			assert isinstance(observer, collections.Callable),"Observer %s must be callable (or need to have the deprecated observe() method)."%(observer)
			self._observers.append(observer)


	def format_fname(self,name): # 0.2.1: renamed from cfnFormatted
		"""
		file name in the configured format (cfnMode).
		
		:returns: String,men-Readable Callers File Name (None is name was None)
		:param name: File file name incl. path, or None
		"""
		if name is None:
			return None
		
		if (self._cfnMode == self.CFN_SHORT):
			"""configured to use minimum name:use file name without directory path """
			res = (name.split("/"))[-1]
			#Cut away ".py" if possible, to shorten the name
			if len(res) > 3:
				if res[-3:]==".py":
					res=res[:-3]
		else:
			assert self._cfnMode == self.CFN_FULL, "unknown value for cfn mode:%s"%(self._cfnMode)
			"""full name:use full path as name"""
			res = name.replace("/","_")
			
		res = res.replace(".","-")		
		return res
	

	def pathAsStr(self, path, imin=0):
		"""
		:param path: iterable
		
			imin: min.index of path to use.
			
		:returns: call path, formatted as str, Empty str if path is empty
		:rtype: str
		"""
		res = ""
		lastWasOmitted = False
		
		for i,(cfn,cln) in enumerate(path):
			
			if i >= imin:
				
				if i==imin:
					res = "|"
					separator = ""
				else:
					separator = "<-"
					
				if cfn is not None:
					# file name and line number are available
					res += "%s%s(%s)"%(separator,self.format_fname(cfn),cln)
					lastWasOmitted = False
				else:
					# a file name to omit
					if not lastWasOmitted: # avoid multiple "<-..."
						res += "<-..."
						lastWasOmitted = True
		return res



	def addClient(self):
		"""
		"""
		pass


	def _timeStr(self, dt):
		"""
		:rtype: str
		:returns: readable time info, based on my _tsFormat
		"""
		if self._tsFormat is None:
			return ""
		else:
			return mStrftime(dt,self._tsFormat)


	def log(self, jobdata):
		"""
		:param jobdata: Internal format. Do not rely on that structure since it will probably remain subject of refactorings.
		"""
#		kwargs = {"pid":pid,"threadname":threadname,"msgid":msgid,"msg":msg,"special":special,"cat":cat,"path":path,"tblen":tblen,"cfunc":cfunc,
#				"formatter":self,"ts":self._timeStr(datetime.now())}
		if len(self._jobhist) >= self._jobhistSize:
			# gain a marginal relieving of the GC:
			# re-use the popped job from history
			# CARE FOR DOCUMENTING jobs cannot be stored in a filter etc.
			job = self._jobhist.pop(0)
			job.__init__(formatter=self,*jobdata)
		else:
			job = MsgJob(formatter=self,*jobdata)
			
		self.logJob(job)


	def logJob(self, job):
		# maintain jobhist queue with current job at [-1]:
		self._jobhist.append(job)

		for i,filter_ in enumerate(self._filters):
			try:
				filter_(jobhist=self._jobhist, writer=self._writer)
			except Exception:
				warn("filter %d:%s failed with %s, LogRecord was: %s. Trace=%s"%(i,filter_,e,job,traceToShortStr()))

		#todo: consider multiple writers aka Handlers
		self._writer.writeNow(job)

		for i,observer in enumerate(self._observers):
			try:
				observer(jobhist=self._jobhist, writer=self._writer)
			except Exception as e:
				warn("observer %d:%s failed with %s, LogRecord was: %s. Trace=%s"%(
					i,observer,
					e,
					job,
					traceToShortStr(6),
					))

