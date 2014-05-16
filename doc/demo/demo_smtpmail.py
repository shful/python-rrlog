#!/usr/bin/env python


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
Demonstrates the basic usage.
@author: Ruben Reifenberg
"""






# Note: That demo is probably not killable with Ctrl-C because of a worker thread which is not marked as Daemon (intentionally)

from rrlog.contrib import mail

# Assume we want mails for these 4 log message categories: 
# I(internal-error), S(ecurity-issue) : we mail these nearly immediately
# E(rror) is business as usual and can wait 60 seconds :)
# W(arnings) are collected at maximum 5 minutes.
rules = (
	mail.CatRule( ("I","S",), 15),
	mail.CatRule( ("E",), 60),
	mail.CatRule( ("W",) ,300),
	)

notifier = mail.mailnotifier(
	mail.SMTPMailer(
		server="smtpserver.example.org", # SMTP server
		serverpw="nobodyknows",
		to_address="receiver@example.org",
		from_address="sender@example.org",
		subject="Vi@gra cheap",
		loginuser="login@example.org", # optional, by default from_address is used
		),
	rules=rules,
	)



# demonstrate with the simple print logger
# observers are available with all log configurations. When remote, observers are in the server side create... function
from rrlog.server import printwriter 
log = printwriter.createLocalLog(
	observers=(notifier,)
	)

# that category will trigger a mail now:
log("Hi my uncle from nigeria like to give yu a million", "S")
