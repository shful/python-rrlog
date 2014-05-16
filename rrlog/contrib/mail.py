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
@summary: Sends emails with a "digest" of selected messages
@author: Ruben Reifenberg
"""

import datetime
import time
import warnings
from threading import Thread, currentThread, RLock, enumerate as threading_enumerate

from rrlog import tool
from rrlog.server import textwriter

now = datetime.datetime.now
timedelta = datetime.timedelta

_spoolers = []


def stop_all():
	"""
	Stops all running spooler threads.
	"""
	for spooler in _spoolers:
		spooler.stop()


def create_observer_smtp(server, serverpw, from_address, to_address, rules, loginuser=None, format_line=None, subject="Log Digest", charset="latin-1", spooler_autostop=True):
	"""
	DEPRECATED
	Use mailnotifier()
	Note: When using the SMTPMailer, watch out for the different parameter order
	
	Creates a mail notifier with a background worker thread.
	Convenience method which sets default values appropriate for many use cases.
	Appends the spooler to the modules spoolers list so that the L{stop_all} function can stop it. 
	:param rules: see L{CatBuffer.__init__}
	:param spooler_autostop: see L{Spooler.__init__}. Defaults to True, so that explicit stop of the spooler threads is not necessary usually.
	:returns: An observer object, intended to be added into the observers list of the log.
	"""
	warnings.warn("use the mailnotifier() function", DeprecationWarning)
	buffer = CatBuffer(rules=rules, format_line=format_line)
	
	mailer = SMTPMailer(
		server=server,
		serverpw=serverpw,
		from_address=from_address,
		to_address=to_address,
		loginuser=loginuser,
		subject=subject,
		charset=charset,
		)
	
	_spoolers.append(
		Spooler(
			mailer=mailer,
			buffer=buffer,
			autostop=spooler_autostop,
			)
		)
	
	return buffer
	

def mailnotifier(mailer, rules, format_line=None, spooler_autostop=True, spooler_sleepsecs=10):
	"""
	Creates a mail notifier with a background worker thread.	
	Creates a spooler and appends it to the modules spoolers list.
	:param mailer: Some object with a method mail(lines)
	See SMTPMailer class for an example, or extend it. 
	:param rules: see L{CatBuffer.__init__}
	:param spooler_autostop: see L{Spooler.__init__}. Defaults to True, so that explicit stop of the spooler threads is not necessary usually.
	:param spooler_sleepsecs: see L{Spooler.__init__}
	:returns: An observer object, intended to be added into the observers list of the log.
	"""
	buffer = CatBuffer(
		rules=rules,
		format_line=format_line,
		)
	
	_spoolers.append(
		Spooler(
			mailer=mailer,
			buffer=buffer,
			autostop=spooler_autostop,
			sleepSecs=spooler_sleepsecs,
			)
		)
	
	return buffer
	

class CatRule(object):
	def __init__(self, cats, max_delay_secs=0):
		"""
		:param max_delay_secs: Maximum time that a message of that categories can be buffered before sending.
		
			High values result in less (but bigger) mails.
			0 == send each line nearly immediately
			
			(Note: The worker thread pauses frequently, causing a littly delay always.
			As a result, multiple messages might be in a mail even with "send immediately".)
			   
		:param cats: tuple of cats to catch, e.g. ("E","S").
		
			None == catch any category (could cause high email traffic)
		"""
		assert not isinstance(cats,str),"cats must be a tuple/list of cat, not '%s'"%(cats)
		self._cats = cats
		self._max_delay_secs = max_delay_secs
		
		
	def max_delay_secs(self, cat):
		"""
		:returns: Max.remaining buffering time for that job. None if rule does not apply.
		"""
		if self._cats is None or cat in self._cats:
			return self._max_delay_secs
		else:
			return None
		
	def __str__(self):
		return "%s[%s:%s secs]"%(self.__class__.__name__,str(self._cats),self._max_delay_secs)
		
		
class Spooler(object):
	"""
	"""	
	def __init__(self, mailer, buffer, sleepSecs=10, autostop=False):
		"""
		Starts a worker thread which reads buffered lines and sends them when their time has come.
		:param sleepSecs: Time to sleep between two are-there-new-lines-checks.
		Set to shorter time if quick reaction is required (for emails probably not needed)
		:param autostop:
		When True, the worker thread will check the number of non-daemon threads after each work interval. 
		When only one (itself) is left, it stops automatically.
		But when there are more threads doing the same trick, explicit stop is required.
		The worker thread won't autostop until the message buffer is completely sent (unlike a daemon thread).  		 
		"""
		self._mailer = mailer
		self._buffer = buffer
		self._sleepSecs = sleepSecs
		self._autostop = autostop
		self._stopped = False
		Thread(target=self.run).start()
	
		
	def _i_am_orphan(self):
		current = currentThread()
		for thread in threading_enumerate():
			if not thread.isDaemon() and (thread is not current):
				return False
		return True
	
	
	def _work(self):
		if self._buffer.deadline_reached():
			lines = list( self._buffer.iter_all_and_clear() )
			self._mailer.mail(lines)
		
		
	def run(self):
		while not self._stopped:
			time.sleep(self._sleepSecs)
			self._work()
			if self._autostop and self._i_am_orphan():
				if self._buffer.size() == 0:
					self.stop()
		self._work()
		
			
	def stop(self):
		"""
		Sets my stop flag, causing the worker thread to finish after its next working interval.
		(All remaining buffered lines are sent before exit.)
		"""
		self._stopped = True
		
		
	def is_active(self):
		return not self._stopped
		

class CatBuffer(object):
	def __init__(self, rules, format_line=None):
		"""
		:param rules: list of rules which decide about the log jobs to send. Use e.g. a tuple of L{CatRule} objects.
		
			If empty, no messages are buffered.
			rules are processed in the given order. If a rule applies, all subsequent rules are ignored.
		"""
		assert hasattr(rules, "__iter__"), "rules must be iterable, not:%s (althought empty list is allowed)"%(type(rules))
		
		if format_line is None:
			format_line = textwriter.defaultFormatter
			
		self._format_line = (format_line,)
		self._lines = []
		self._rules = rules		
		self._deadline = None
		self._rlock = RLock()
		
		
	def _calc_deadline(self, secs_remaining):
		return now() + timedelta(seconds=secs_remaining)
	

	def __call__(self, jobhist, writer):
		"""
		The current implementation locks the current thread if a rule applies, to safely buffer it.
		"""
		currentJob = jobhist[-1]
		
		for rule in self._rules:
			secs = rule.max_delay_secs(currentJob.cat)
			
			if secs is not None:
				self._rlock.acquire()
				self._buffer(currentJob, secs)
				self._rlock.release()
				return
			
				
	def _buffer(self, job, secs):
		self._lines.append(
			(job.cat, self._format_line[0](job,"")) # "" for no linecount
			)
		deadline = self._calc_deadline(secs)
		
		if self._deadline is None or deadline < self._deadline:
			self._deadline = deadline
			
			
	def iter_all_and_clear(self):
		"""
		:returns: tuples (cat, linetext)
		"""
		self._rlock.acquire()
		
		for cat,text in self._lines:
			yield cat,text
			
		self._lines = []
		self._deadline = None
		self._rlock.release()
					

	def deadline_reached(self):
		return (self._deadline is not None) and (now() >= self._deadline)

	
	def size(self):
		return len(self._lines)


class SMTPMailer(object):
	"""
	Provides a way to send SMTP mails with simple user:password authentication. 
	This mailer has no advanced authentication methods like starttls.
	"""
	def __init__(self, server, serverpw, to_address, from_address, subject="Log Digest", loginuser=None, charset="latin-1"):
		"""
		:param subject: serves as a default. The mail method may dynamically create a better one.
		"""
		if loginuser is None:
			loginuser = from_address
		self._server = server
		self._serverpw = serverpw
		self._to_address = to_address
		self._from_address = from_address
		self._loginuser = loginuser
		self._default_subject = subject
		self._charset = charset
		
		
	def _content_and_subject(self, lines):
		def lines_():
			for cat, line in lines:
				yield line+"\n"
				
		return "".join(lines_()), self._default_subject
		
		
	def mail(self, lines):
		"""
		Override to use another mail method, e.g. for other SMTP login protocols
		Override to create other mail contents or subjects
		(for example, we want to put the cats into the subject line)
		"""
		content, subject = self._content_and_subject(lines)
		tool.mail_smtp(
			server = self._server,
			serverpw = self._serverpw,
			to_address = self._to_address,
			from_address = self._from_address,
			loginuser = self._loginuser,
			subject = subject,
			content = content,
			charset = self._charset,
			)
