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
Indent message texts depending on callers stack depth.
@author: Ruben Reifenberg
"""

from rrlog.tool import StrIndenter


def format_line(job, lineCount):
	"""
	The default formatter that removed everything except the pure message
	"""
	return job.msg+"\n"

class StackIndentFilter(object):
	"""
	Adjusts itself to zero indention with the first log call.
	You can re-adjust (tara) with later log calls. 

	Use	log( ..., stackindent_tara=0).
	This will adjust the current call to be zero-indented.
	
	Use -1 to immediately indent by 1 token etc.
	(Negative indention is ignored, such lines appear with indent zero.)
	"""
	def __init__(self, token=" ",msgPrefix=None):
		"""
		:param token: The string used to indent one level.
		:param msgPrefix: str. If given, indent only messages 
		
			starting with this prefix.
			All other messages are ignored (they cannot even trigger a "tara").
		"""
		self._si = StrIndenter(token=token)
		self._dotara = True
		self.msgPrefix = msgPrefix
		

	def __call__(self, jobhist, writer):
		job = jobhist[-1]

		if self.msgPrefix is not None:
			# ignore jobs without the right msg prefix
			if not job.msg.startswith(self.msgPrefix): return

		# do tara in two cases:
		# when we get the first call, or
		# when we get a tara request with the job
		try:
			tara = job.special["stackindent_tara"]
			self._dotara = True
		except KeyError:
			if self._dotara:
				tara = 0
				
		if self._dotara:
			self._si.tara(job.tblen, tara)
			self._dotara = False
			
#		print "job.tblen=%s (%s,%s)"%(job.tblen,job.msg,str(job.path))
		job.msg=self._si(job.tblen)+job.msg


def createPrintIndentLog(token="  ", format_line=format_line, **kwargs):
	"""
	convenience function for
	"log to standard out and indent."
	By default, the messages are formatted to contain nothing but the message string (no timestamp etc.)
	
	:param token: str, the indention token
	:returns: local log
	"""
	from rrlog.server.printwriter import createLocalLog
	
	return createLocalLog(
		filters=(StackIndentFilter(token=token),),
		format_line=format_line,
		**kwargs
		)
