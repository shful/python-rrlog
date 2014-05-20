# -*- coding: utf-8 -*-

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
Test the tool module.
Requires py.test from the PyPy project.
@author: Ruben Reifenberg
"""
from datetime import datetime
from rrlog.tool import *
from rrlog.tool import _cutcount

def test_mStrftime():
	d = datetime(2007,5,10,10,16,59,123456)
	assert mStrftime(d,"%3N") == "123", "got "+mStrftime(d,"%3N")
	assert mStrftime(d,"%Y-%3N") == "2007-123"
	assert mStrftime(d,"%3N-%Y") == "123-2007"

def test_ListRotator():
	r = ListRotator(())
	import py
	py.test.raises(IndexError, r.__next__)

	r = ListRotator((None,))
	assert r.__next__() == None
	assert r.__next__() == None

	r = ListRotator((None,77))
	assert r.__next__() == None
	assert r.__next__() == 77
	assert r.__next__() == None
	assert r.__next__() == 77

def test_cutcount():
	assert _cutcount(0,0)==0
	assert _cutcount(0,1)==0
	assert _cutcount(1,0)==2 #impossible: 1 to cut + 1 digit
	assert _cutcount(10,10)==0
	assert _cutcount(10,9)==2
	assert _cutcount(10,8)==3
	assert _cutcount(100,99)==2
	assert _cutcount(100,92)==9
	assert _cutcount(100,91)==11
	assert _cutcount(100,90)==12
	assert _cutcount(100,89)==13
	assert _cutcount(100,3)==99
	assert _cutcount(100,2)==101 #impossible again

# def test_lu2a():
# 	assert lu2a(None)==None
# 	assert lu2a("")==""
# 	assert lu2a("ä", 1000)=="\\xe4"
# 	assert lu2a("abc", 3, "?!?")=="abc"
# 	assert lu2a("abcd", 3, "??")=="??"
# 	assert lu2a("abcde", 4)=="[5+]"
# 	assert lu2a("aÄ")==r"a\xc4", "got "+lu2a("aÄ")+"."
# 	assert lu2a("ÄÖöß", 9)==r"\xc4[12+]"
# 	assert lu2a("ÄÖÜäöüßxy", 9)==r"\xc4[26+]"
# 	assert lu2a("xÄÖÜäöüßy", 9)==r"x\xc[26+]"
# 
# def test_lu2a_de():
# 	assert lu2a_de(None)==None
# 	assert lu2a_de("")==""
# 	assert lu2a_de("\u00b5ÄÖÜäöüß",50)=="\\xb5AEOEUEaeoeuess"
# 	assert lu2a_de("ÄÖÜäöüß", 4, "???")=="???"
# 	assert lu2a_de("ÄÖÜäöüß", 5)=="[14+]"
# 	assert lu2a_de("ÄÖÜäöüß", 6)=="A[13+]"
# 	assert lu2a_de("ÄÖÜäöüß", 7)=="AE[12+]"
# 	assert lu2a_de("xÄÖÜäöüß", 7)=="xA[13+]"
# 	assert lu2a_de("xÄÖÜäöüß\u00bf", 7)=="xA[17+]"


if __name__ == "__main__":
	import sys
	from rrlog.test import run
	#run(sys.argv[0],k="test_indi")
	run(sys.argv[0])
