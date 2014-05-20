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
The XML-RPC version of a LogServer connection.
This is a slow way to log
(mainly because of the unnecessary overhead of
xml-rpc blocking calls), but simple and robust.
Use it when the performance is good enough for you.
@author: Ruben Reifenberg
"""
import pickle
from rrlog import globalconst
#todo: rename -> xmlrpcserver; Keep package xmlrpc as transition package
try:
	#Py3:from xmlrpc.server import SimpleXMLRPCServer
	#Py2:from SimpleXMLRPCServer import SimpleXMLRPCServer
	from xmlrpc import server as xserver
except ImportError:
	import SimpleXMLRPCServer as xserver


class LogAdapter(object):
	"""
	"""
	def __init__(self, logServer):
		"""
		:returns: "" if all right, error msg if not
		"""
		self.s = logServer

	def log(self, logdata_ps): # 0.2.2: single arg as for non-xmlrpc version
		"""
		No threading, xmlrpc blocks until return
		"""
		try:
			logdata = pickle.loads(logdata_ps.data)
		except Exception as e:
			return "invalid pickle data:"+str(e)
		try:
			self.s.log(logdata)
		except Exception as e:
			return "log failed:"+str(e)
		return ""
		

	def addClient(self):
		"""
		:rtype: int
		:returns: unique id
		"""
		self.s.addClient()
		return 0


def createSimpleXMLRPCServer(host, ports):
	"""
	Creates server that does no multithreading.
	Remark: The SimpleXMLRPCServer seems to do no multithreading,
	except we use MixIn class.
	Indeed, I found that a second client
	is blocked as long as the server is processing another request.
	(Python 2.4)
	:param ports: list or iterator of port numbers
	Multiple ports address the problem that a socket is for some time
	"already in use" when restarting the server.
	The first free port of the ports is used.
	"""
	for port in ports:
		try:
			res = xserver.SimpleXMLRPCServer((host,port))
		except Exception as e:
			print("Retrying:%s"%(e))
		else:
			res.logRequests = 0 # hint from newsgroup to disable the  - - [13/Apr/2007 13:33:57] "POST /RPC2 HTTP/1.0" 200 - output with every request
			return res



def startServer(logServer, host="localhost", ports=(globalconst.DEFAULTPORT_XMLRPC,), readyMsg=True):
	"""
	Run the given logServer as an xmlrpc server (forever).
	:param ports: see L{createSimpleXMLRPCServer}
	"""
	# v0.3.0: The order of host,ports has changed for consistency
	# warn:
	if type(host) in (tuple,list) or type(ports) in (str,str):
		msg = "Unexpected host or ports type. Note: The argument order in startServer has changed. Use host,ports now instead of ports,host. That has been inconsistent before (sorry)"
		warnings.warn(msg)
		raise TypeError(msg)
	
	server = createSimpleXMLRPCServer(host,ports)
	adapter = LogAdapter(logServer)
	server.register_function(adapter.log, "log")
	server.register_function(adapter.addClient, "addClient")
	if readyMsg: print("log server ready. Available at host,port: %s"%(str(server.server_address)))
	server.serve_forever()
