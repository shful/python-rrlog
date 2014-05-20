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
The client (i.e.application) side of an XMLRPC log connection.
@author: Ruben Reifenberg
"""

import pickle
from xmlrpc.client import ServerProxy, Error, Binary

import rrlog
from rrlog import globalconst


class XMLRPCLogException(Exception):
	def __init__(self, txt, msgid):
		"""
		:param txt: some ascii error explanation text
		:param msgid: msgid of the log-msg that caused the problem.
		"""
		Exception.__init__(self, txt+"[msgid%s]"%(msgid))


class XMLRPCConnectionException(XMLRPCLogException):
	"""
	Logging went wrong because of a connection issue.
	"""
	pass


class XMLRPCServerException(XMLRPCLogException):
	"""
	Logging went wrong because the server had a problem.
	"""
	pass


def loglog(msg, cat=""):
	"""
	Deactivated, activate for debugging only.
	Here does the log logging itself.
	"""
	pass
	print("log:%s %s"%(cat,msg))#todo:weg


def connect(host, ports):
	"""Steve Holden,http://www.velocityreviews.com/forums/t539476-xml-rpc-timeout.html:
	The easiest way is to use socket.setdefaulttimeout() to establish a
	longer timeout period for all sockets, I guess. It's difficult to
	establish different timeouts for individual sockets when they aren't
	opened directly by your own code (though each socket does also have a
	method to set its timeout period).
	---
	Sh...We must not modify sockets globally in a library like rrlog.
	We can't use signal, since we usualy don't have the main thread.
	We can't rely on a specific Python version and OS which would enable more solutions.
	The xmlrpc lib should be more cooperative :-(
	=> No timeout solution currently.
	"""
	for port in ports:
		server = ServerProxy("http://%s:%s"%(host,port))
		
		try:
			server.addClient()
		except Exception as e:
			loglog("Connect: no server at port%s:%s"%(port, e))
		else:
			loglog("Found server at %s/%s"%(host, port))
			return server
		
	raise Exception("no server at %s%s"%(host,str(ports)))


class LogServerProxy(object):
	"""
	First method call must be addClient,
	since this establishes the server connection.
	"""
	def __init__(self, host, ports):
		"""
		"""
		self.host = host
		self.ports = ports


	def addClient(self): # Refactoring. addClient is to be removed
		"""
		Does the connection to the server.
		"""
		self.server = connect(self.host,self.ports)


	def log(self, logdata):
		
		try:
			ok = self.server.log(
				Binary(pickle.dumps(logdata))
				)
		except Exception as e:
			raise XMLRPCConnectionException("%s"%(e),msgid=logdata[0])
		else:
			if ok != "":
				raise XMLRPCServerException(ok,msgid=logdata[0])


def createClientLog(host="localhost", ports=(globalconst.DEFAULTPORT_XMLRPC,), errorHandler=None, traceOffset=0, stackMax=5, extractStack=True, seFilesExclude=None):
	"""
	:returns: Log instance
	"""
	return rrlog.Log(
		server = LogServerProxy(host, ports),
		traceOffset=traceOffset,
		stackMax = stackMax,
		errorHandler=errorHandler,
		seFilesExclude=seFilesExclude,
		extractStack=extractStack,
	)

