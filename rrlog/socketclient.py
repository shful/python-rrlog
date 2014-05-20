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





from logging import handlers
import struct

import rrlog
from rrlog.globalconst import remotedumps,warn
from rrlog import globalconst


class SerializeError(Exception):
	pass


class _SocketHandler(handlers.SocketHandler):
	
	def makePickle(self, record):
		"""
		Pickles the record in binary format with a length prefix, and
		returns it ready for transmission across the socket.
		"""
#        ei = record.exc_info
#        if ei:
#            dummy = self.format(record) # just to get traceback text into record.exc_text
#            record.exc_info = None  # to avoid Unpickleable error
#        s = pickle.dumps(record.__dict__, 1)
		try:
			s = remotedumps(record)
		except Exception as e:
			raise SerializeError(""""serialize log data: %s failed with:%s.\n
				A possible reason is the usage of json or similar library (e.g. marshal)
				which cannot serialize custom objects. Use basic datatypes (mubers,strings,containertypes) in this case,
				or configure logging to use another serialize library (see manual).
				"""%(record,e))
#        if ei:
#            record.exc_info = ei  # for next handler
		slen = struct.pack(">L", len(s))
		return slen + s
	
	
	def ping_seems_possible(self):
		"""
		The handlers.SocketHandler should have a valid "sock" Attribute after we sent something.
		If not, an error occurred.
		:returns: True a simple method call on the server worked without error
		"""
		self.emit("ping")
		return self.sock is not None



class LogServerProxy(object):
	def __init__(self, host, ports):
		"""
		"""
		self.connectedInitially = False
		for port in ports:
			handler = _SocketHandler(host,port)
			if handler.ping_seems_possible():
				self.connectedInitially = True
				break
				
		if not self.connectedInitially:
			port = ports[0]
			warn("""! Loosing Log Messages ! Currently, no rrlog server is found at %(h)s and any of these ports: %(ps)s.
				Remote-Logging to port %(p)s now. Until a server starts with this port, log messages get lost."""%(
					{"h":host,"ps":ports,"p":port}
					)
				)
			handler = _SocketHandler(host,port)
			
		self.handler = handler


	def addClient(self):
		"""
		"""
		return 0


	def log(self, logdata):
		self.handler.emit(logdata)



def createClientLog(host="localhost", ports=(globalconst.DEFAULTPORT_SOCKET,), errorHandler=None, traceOffset=0, stackMax=5, extractStack=True, seFilesExclude=None):
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


if __name__ == "__main__":
	import logging
	rootLogger = logging.getLogger('')
	rootLogger.setLevel(logging.DEBUG)
	socketHandler = _SocketHandler('localhost',
						logging.handlers.DEFAULT_TCP_LOGGING_PORT)
	# don't bother with a formatter, since a socket handler sends the event as
	# an unformatted pickle
	rootLogger.addHandler(socketHandler)

	print("send...")
	for i in range(0,10000):
		rootLogger.info("Das Pferd frisst...")
		rootLogger.info("...keinen Gurkensalat.")
	print("...send done.")
