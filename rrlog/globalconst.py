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


from warnings import warn # override for different warn target



class EnvironmentError(Exception):
	"""
	Something's wrong with the runtime environment
	"""
	pass


try:
	import simplejson as json # currently, simplejson seems faster.
except ImportError:
	try:
		import json as json
	except ImportError as e:
		try:
			from rrlog import fbsimplejson as json # fallback json version, packaged here.
		except ImportError as e:
			raise EnvironmentError(
				"""%(m)s:No json or simplejson library was found.\n
				json is core library since Python 2.6; earlier versions need separate json installation.
				Alternatively, rrlog can be configured to use another library like marshal or pickle.
				See manual or source code of module %(m)s for "howto" and potential security caveats.
				"""%{"m":__name__})


# these values should work as alternative to json.dumps:
# marshal.dumps
# lambda x: pickle.dumps(x,1)
remotedumps = json.dumps

# these values must correspond with the above ones:
# marshal.loads
# pickle.loads
remoteloads = json.loads

# Remarks:
# marshal is fast but may require both sides to run with same Python version; security is unknown.
# pickle is unsecure when unpickling.
# You may also check the "cerealizer" library.


# remote logging server/client will use these ports by default
# Python logging.handlers is on 9020+
DEFAULTPORT_SOCKET = 9801
DEFAULTPORT_XMLRPC = 9804
