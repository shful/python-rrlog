# Copyright (c) 2007 Ruben Reifenberg.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#    
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
@summary:
logging classes with a richer interface
for convenience.
@author: Ruben Reifenberg
"""

import sys,traceback


class RichLog1(object):
	"""
	A wrapper for rrlog.Log.
	It adds functionality (convenience methods)
	It cannot be wrapped again (Doesn't behave exactly like the wrapped log.)
	@ivar wrapped: the wrapped log object.
	"""
	def __init__(self, log):
		"""
		:param log: The rrlog.Log to wrap.
		
			Increases the traceOffset of log (+1).
		"""
		self.wrapped = log
		self.wrapped.traceOffset += 1

	def __call__(self, *args, **kwargs):
		"""
		only delegates to the wrapped log
		"""
		self.wrapped(*args, **kwargs)

	def log(self, *args, **kwargs):
		"""
		REMOVED: The log.log() is removed. Use log().
		"""
		self.wrapped.log(*args, **kwargs)

	def trace(self, message="", use_ex=False):
		"""
		logs message plus a stacktrace (each stack line as a single log message.)
		Can use the current trace, of the trace of the last exception.
		:param use_ex: If False, I use the current stacktrace. If True, I use the existing sys.exc_info().
		"""
		self.wrapped("%s,trace:"%(message))
		if use_ex:
			type,value,exc_trace = sys.exc_info()
			trace=traceback.extract_tb(exc_trace)
		else:
			trace = traceback.extract_stack()
		lines = traceback.format_list(trace)
		for i,line in enumerate(lines):
			self.wrapped("[%s] %s"%(i,line))


	def dict(self, aDict, message=""):
		"""
		logs a dict, each item as a single log msg
		:param message: Optional log message e.g. to identify the dict
		"""
		self.wrapped("%s,dict:"%(message))
		for i,(k,v) in enumerate(list(aDict.items())):
			self.wrapped("[%s] %s:%s"%(i,k,v))
