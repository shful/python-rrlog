
import time
from rrlog.contrib.mail import *
from rrlog.contrib import mail



class Mailer(object):
	expecteds = [
		("W","Hello"),
		("E","World")
		]
	
	def __init__(self):
		self.hasMailed = False
		
	def mail(self, lines):		
		for i,(cat,text) in enumerate(lines):
			assert cat == self.expecteds[i][0]
			assert text == self.expecteds[i][1]
		self.hasMailed = True


def format_line(job, lineCount):
	return job.msg


class Job(object):
	def __init__(self, cat, msg):
		self.msg=msg; self.cat=cat
		

def test_catbuffer_0():
	""" empty rules """
	rules=()
	b = CatBuffer(rules=rules, format_line=format_line)
	
	assert not b.deadline_reached()
	b([Job("E","hi")],None)
	assert b.size() == 0
	
	
def test_catbuffer_1():
	""" single rule """
	rules=(
		CatRule(("E",),0),
		)
	b = CatBuffer(rules=rules, format_line=format_line)
	
	assert not b.deadline_reached()
	b([Job("E","hi")],None)
	assert b.size() == 1
	b([Job("E","hi")],None)
	assert b.size() == 2
	
	
def test_catbuffer_catchall():
	""" single "catchall" rule """
	rules=(
		CatRule(None,100),
		)
	b = CatBuffer(rules=rules, format_line=format_line)
	
	assert not b.deadline_reached()
	b([Job("E","hi")],None)
	assert b.size() == 1
	b([Job("E","hi")],None)
	assert b.size() == 2
	
	
def test_catbuffer_deadlines():
	""" 2 rules, check deadlines """
	oldnow = mail.now
	oldtimedelta = mail.timedelta
	
	mail.timedelta = lambda seconds: seconds
	mail.now = lambda: 100
	rules=(
		CatRule(("E",),100),
		CatRule(("","W"),10),
		)
	b = CatBuffer(rules=rules, format_line=format_line)
	
	assert not b.deadline_reached()
	
	# 1 job with 100 secs
	b([Job("E","hi")],None)
	assert b.size() == 1
	assert not b.deadline_reached()
	mail.now = lambda: 199
	assert not b.deadline_reached()
	mail.now = lambda: 200
	assert b.deadline_reached()
	for x in b.iter_all_and_clear(): pass
	assert b.size() == 0
	assert not b.deadline_reached()
	
	# 2 jobs with 100 and 10 secs
	mail.now = lambda: 100
	b([Job("","ho")],None)
	b([Job("E","hi")],None)
	assert not b.deadline_reached()
	mail.now = lambda: 110
	assert b.deadline_reached()
	
	mail.now = oldnow
	mail.timedelta = oldtimedelta
	

def test_whole():
	rules=(
		CatRule(("E",),1),
		CatRule(("","W"),1),
		)
	mailer = Mailer()
	notifier = mail.mailnotifier(
		mailer,
		rules=rules,
		format_line=format_line, 
		spooler_sleepsecs=0.1,
		)
	from rrlog.server import printwriter 
	log = printwriter.createLocalLog(
		observers=(notifier,),
		)
	log("Hello","W")
	log("Not mail that","Y")
	log("World","E")
	log("Not mail that","X")

	d = 0.1
	secs = 0.0
	while 1:
		time.sleep(d)
		secs += d			
		if mailer.hasMailed:
			break
		if secs > 10:
			mail.stop_all()
			assert False
			
	mail.stop_all()


if __name__ == "__main__":
	import sys
	from rrlog.test import run
	#run(sys.argv[0],k="test_whole")
	run(sys.argv[0])
