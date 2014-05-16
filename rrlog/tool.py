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
@summary: Tools not specific for logging purpose
@author: Ruben Reifenberg
"""
import time


class ListRotator(object):
	"""
	Iteriert durch eine gegebene Liste, beginnend mit erstem Element.
	beginnt im Gegensatz zum Iterator wieder von vorn.
	@ivar i: index of last returned element
	"""
	def __init__(self, list):
		"""
		:param list: len >=1
		
			list needs to be constant (behaviour not defined for later changes)
			
		"""
		self.list = list
		self.i = -1

	def next(self):
		"""
		Not threadsafe.
		:returns: next list element, rotating
		:raises IndexError: if list has length 0
		"""
		self.i += 1
		if self.i >= len(self.list):
			self.i = 0
		return self.list[self.i]

	def len(self):
		return len(self.list)
	

def _cutcount(l, max):
	"""
	How many elements to cut away from something with len l,
	when we want restlen+len(decimal-digit-of-cut-count) < max?
	:rtype: int
	:returns: count of chars to cut away (cutcount) (can be > l when max is too low)
	"""
	if l<=max: return 0
	else:
		cdl=1 #cutcount digit len (e.g. 3 for 100..999)
		cut=10 #always 10^cdl
		while True:
			if l-cut+cdl<max:
				return l-max+cdl
			cut=cut*10
			cdl+=1


def lu2a(unistr, max=50, errorstr="~~~"):
	"""
	Limited Unicode To Ascii (limited: the result length is limited)
	Intended for ASCII-logging of untrusted (e.g.user input) unicode strings.
	The length limitation is intended for storage in length-limited ASCII Database fields.
	:rtype: ASCII str or None
	:returns: The argument but with: All non-ascii chars replaced by "\\xhexvalue".
	If N chars (of the result string) are thrown away, "[N+]" is appened at the end.
	:param unistr: Python Unicode or None
	:param max: >=3, length limit of the RESULT STRING (default 50)
	:param errorstr: Returned in case max is too low to return the regular result.
	"""
	assert max >= 3
	if unistr is None: return None
	res = unistr.encode("ascii","backslashreplace")
	if len(res)>max:
		cutcount = _cutcount(len(res),max-3) #3 because "[+]"
		if cutcount<=len(res):
			res = "%s[%d+]"%(res[:-cutcount],cutcount)
		else:
			#max is too low to display even the count of cut chars
			res = errorstr
	return res


def lu2a_de(unistr, max=50, errorstr="~~~"):
	"""
	Note: In case of unistr containing non-ascii characters, this method
	gets slow (because it does a python loop over each character.)
	@see: lu2a
	Additionally, the german umlauts are replaced by AE,OE...
	to make it more readable (by the drawback of information loss, of course.)
	"""
	assert max >= 3
	if unistr is None: return None
	try:
		# fastest if possible
		res = unistr.encode("ascii")
	except UnicodeError:
		# slow.
		# Could be faster. But this wants to be is a side effect free library
		# and we don't want to register a callback handler in codecs globally.
		res = ""
		for char in unistr: #don't care for speed. Assume this is seldom.
			try:
				res += char.encode("ascii")
			except UnicodeError:
				try:
					res += {
						u"\u00e4":"ae",
						u"\u00f6":"oe",
						u"\u00fc":"ue",
						u"\u00c4":"AE",
						u"\u00d6":"OE",
						u"\u00dc":"UE",
						u"\u00df":"ss",
						}[char]
				except KeyError:
					res += char.encode("ascii","backslashreplace") #"<%d>"%(ord(char))
	if len(res)>max:
		cutcount = _cutcount(len(res),max-3) #3 because "[+]"
		if cutcount<=len(res):
			res = "%s[%d+]"%(res[:-cutcount],cutcount)
		else:
			#max is too low to display even the count of cut chars
			res = errorstr
	return res


def mStrftime(dt, formatStr):
	"""
	:param dt: datetime.datetime
	:param formatStr: strftime format string for dt
		with an extension: %3N is milliseconds
		
	:returns: str, made by dt.strftime
	"""
	formatStr = formatStr.replace("%3N",str(dt.microsecond/1000))
	return dt.strftime(formatStr)


def tm_strftime(format, t, ms):
	"""
	:param t: 9-tuple, as returned by time.localtime()
	:param format: strftime format string
		with an extension: %3N is milliseconds
	:param ms: microseconds as int (0..999)
	
	:returns: str, made by time.strftime
	"""
	format = format.replace("%3N",str(ms))
	return time.strftime(format, t)


def traceToShortStr(maxLines=3,exc_info=None,use_cr=True):
	"""
	:param exc_info: as given by sys.exc_info(). If None, it is obtained by calling sys.exc_info
	:param use_cr: If True, "\\n" is used between the path lines. Otherwise, "<" will separate the lines.
	
	:returns: short str describing the current ex.stacktrace (end-first),
		"" if there is no current exc.
	"""
	import sys,traceback
	
	if exc_info is None:
		type,value,exc_trace = sys.exc_info()
	else:
		type,value,exc_trace = exc_info[0],exc_info[1],exc_info[2]
		
	if use_cr:
		sep = "\n"
	else:
		sep = "<"
		
	trace=traceback.extract_tb(exc_trace)
	lines = traceback.format_list(trace)
	res = "" # for maxLines==0 or no exception traceback available
	
	for i in range(0, len(lines)):
		
		if i==maxLines:
			break
		
		if i==0:
			res = "%s%s%s"%(value,sep,lines[-i-1]) #order beginning with end
		else:
			res += "%s%s"%(sep,lines[-i-1])
		
	return res


class StrIndenter(object):
	"""
	Create a String consisting of "depth" identical tokens.
	Intended for output indention.
	"""

	def __init__(self, token=" ", offset=0):
		"""
		:param token: str. The resulting string will consist of this tokens.
		"""
		self.tara(offset) #self._offset = 0
		self.token = token


	def tara(self, depth, tara=0):
		"""
		set string/indention lengt 0 for the current stack depth
		:param tara: is added to depth (depth:=depth+tara instead of explicit tara has the same result)
		"""
		self._offset = depth+tara
		

	def __call__(self, depth):
		"""
		:returns: string, consisting of the given tokens
		"""
		return self.token * (depth-self._offset)


def mail_smtp(server,serverpw,to_address,from_address,loginuser,subject,content,charset="latin-1"):
	"""
	Send subject/content, as latin-1 by default
	String-Parameter; subject/content may be unicode or str.
	
	:returns: None
	
	:param server: e.g.."mail.gmx.net"
	:param serverpw: SMTP server password
	"""
	import sys
	import smtplib
	import socket
	from email.MIMEText import MIMEText
	
	try:
		server = smtplib.SMTP(server)
		#server.set_debuglevel(1)
	except socket.gaierror:
		e,f,g = sys.exc_info()
		msg = "ERROR:%s,%s \n%s"%(e,f, traceToShortStr())
		sys.stderr.write(msg)
		sys.stderr.write("(Network down? No DNS resolution?)")
		return
	except:
		e,f,g = sys.exc_info()
		msg = "ERROR:%s,%s \n%s"%(e,f, traceToShortStr())
		sys.stderr.write(msg)
		return
		
	try:
		server.login(loginuser, serverpw)
	except:
		e,f,g = sys.exc_info()
		msg = "ERROR login:%s,%s\n%s"%(e,f, traceToShortStr())
		sys.stderr.write(msg)
		return

	msg = MIMEText(content,_charset=charset)
	msg["From"] = from_address
	msg["To"] = to_address
	msg["Subject"] = subject
	
	try:
		server.sendmail(from_address, (to_address,), msg.as_string())
	except:
		e,f,g = sys.exc_info()
		msg = "ERROR sendmail:%s,%s"%(e,f)
		sys.stderr.write(msg)
		msg = u"ERROR sendmail; server=%s, from=%s, to=%s"%(server, from_address, to_address)
		sys.stderr.write(msg.encode("ascii","backslashreplace"))
		
	try:
		server.quit()
	except:
		e,f,g = sys.exc_info()
		print "ERROR quit:%s,%s"%(e,f)
