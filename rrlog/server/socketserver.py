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
Besides the thread(s) reading the socket, there is a single worker thread which feeds the log server.
To stop the threaded server process (Ctrl-C prbably won't work) 
use the specified module variables to regularly end it without log line loss, or kill the process.
"""


import sys
import logging.handlers
import SocketServer
import struct
import threading
import collections
import socket
import datetime
import time

from rrlog.globalconst import remoteloads,warn
from rrlog import globalconst

maxlen_jobdataq = 100000
socketreceiver = None # .abort=True in the LogRecordSocketReceiver to exit
rrlog_server = None
jobdataq = collections.deque() # alt: Queue.Queue
processq_stop = False # to exit the worker thread
counter = 0


def _i_am_orphan():
	# siehe rrlog.mail.py, wenn wirklich genutzt, kann sie zu rrlog.tool.i_am_orphan_thread werden
	current = threading.currentThread()
	for thread in threading.enumerate():
		if not thread.isDaemon() and (thread is not current):
			return False
	return True


def processq():
	"""
	Loop which forever
	pops the oldest (left) element from the jobdataq and calls the log server.
	The global variable processq_stop=True ends the loop, but not before the jobdataq is found empty.
	"""
	while True:
		try:
			pickled = jobdataq.popleft()
		except IndexError:
			if processq_stop or _i_am_orphan():
				return
		else:
			try:
				jobdata = remoteloads(pickled)
			except Exception,e:
				# no exit. there may be a process sending erroneously to me
				warn("serialization protocol error: deserialize jobdata failed; a job is skipped (%s)"%e)
			else:
				if "ping" == jobdata:
					# Someone wants to know whether I'm alive
					pass
				else:
					rrlog_server.log(jobdata)


class LogRecordStreamHandler(SocketServer.StreamRequestHandler):
	"""Handler for a streaming logging request.

	This basically logs the record using whatever logging policy is
	configured locally.
	"""

	def handle(self):
		"""
		Handle multiple requests - each expected to be a 4-byte length,
		followed by the LogRecord in pickle format. Logs the record
		according to whatever policy is configured locally.
		"""
		#raise ValueError("merkt der Client das?") nein, der Client merkt nix, und blockiert auch nicht.
		overfull_warned = False # i've already emitted an overfull warning
		
		while True:
			chunk = self.connection.recv(4)
			
			if len(chunk) < 4:
				break
			
			slen = struct.unpack(">L", chunk)[0]
			try:
				chunk = self.connection.recv(slen)
			except MemoryError:
				# already seen when connecting an XMLRPC client by mistake ...
				sys.stderr.write("corrupt data, did you use the right socket client ?")
				raise
			
			while len(chunk) < slen:
				chunk = chunk + self.connection.recv(slen - len(chunk))
				
#			obj = self.unPickle(chunk)
#			self.rrlog_server.log(obj)

			if len(jobdataq) <= maxlen_jobdataq: # deque of python2.6 has maxlen but that throws away oldest elements
				jobdataq.append(chunk)
			elif not overfull_warned:
				# this is not exact with multiple threads (e.g.ThreadedTCPServer). 
				# But without harm because, when getting near the queue size limit, arbitrary jobs will be skipped in any case.
				warn("skipping job because queue len > %s. Subsequent warnings of that type are disabled."%maxlen_jobdataq) # may appear >1 times with >1 threads
				overfull_warned = True



# there is also SocketServer.ThreadingTCPServer
# but should a log really load multiple cpu cores ?
# moreover, that would require the rotation to be threadsafe
tcpservercls = SocketServer.TCPServer


class LogRecordSocketReceiver(tcpservercls):
	"""simple TCP socket-based logging receiver suitable for testing.
	"""

	allow_reuse_address = 1

	def __init__(self, host, ports,	handler=LogRecordStreamHandler):
		
		for port in ports:
			try:
				tcpservercls.__init__(self, (host, port), handler)
			except socket.error,e:
				warn("port %s not available:%s"%(port, e))
				port = None
				
		if not port:
			raise

		self.abort = 0
		self.timeout = 1
		self.logname = None
		self.host = host
		self.port = port


	def serve_until_stopped(self):
		import select
		abort = 0
		while not abort:
			
			rd, wr, ex = select.select(
				[self.socket.fileno()],
				[],
				[],
				self.timeout
				)
			
			if rd:
				self.handle_request()

			abort = self.abort


def startServer(logServer, host="localhost", ports=(globalconst.DEFAULTPORT_SOCKET,)):
	"""
	Run the given logServer as an xmlrpc server (forever).
	:param ports: sequence of portnumbers, at least one number. The first port available is used.
	
		Multiple ports is for development, where sometimes ports may remain blocked.
		In production, better use a single port only, for best control over which server/client pairs are married.
	"""
	global socketreceiver
	global rrlog_server
	
	rrlog_server = logServer
	socketreceiver = LogRecordSocketReceiver(host, ports)
#	print("About to start TCP server...")
	
	import os
	t = threading.Thread(target=processq)	
	t.start()
	print "%s:log server ready. Available at host,port: %s.Pid=%s, thread.ident=%s"%(
		datetime.datetime.now(),
		str( (socketreceiver.host, socketreceiver.port)),		
		os.getpid(),
		t.ident
		)
	
	socketreceiver.serve_until_stopped()



