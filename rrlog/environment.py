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
constants about the environment (SQLAlchemy) available
Purpose: provide compatibility with a wide SQLAlchemy version range
@author: Ruben Reifenberg
"""

try:
	import sqlalchemy
	sa_available = True
except:
	sa_available = False

if sa_available:
	try:
		v = sqlalchemy.__version__
	except AttributeError:
		# older 0.3.x has no __version__ attribute
		# assume old 0.3.x. Not prepared for 0.2.x and older.
		v = "0.3.x"

	if v.startswith("0.3."):
		# SA exactly 0.3.x
		sa_v0_3_x = True
	else:
		sa_v0_3_x = False

	if v.startswith("0.3.") or v.startswith("0.4.") or v.startswith("0.5."):
		# SA lower than 0.6.0
		sa_lt_v0_6_0 = True
	else:
		sa_lt_v0_6_0 = False
