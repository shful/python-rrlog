.. rrlog documentation master file, created by
   sphinx-quickstart on Thu May 23 14:13:55 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


.. _SqlAlchemy: http://www.sqlalchemy.org
.. _Sourceforge: http://sourceforge.net/projects/rrlog/
.. _Github: https://github.com/shful/python-rrlog


Manual for rrlog
*************************************************


*A Remote Rotating Log for Python that works instantly*


----

Download from `Github`_ | `Sourceforge`_ | see :ref:`changes`



Overview
=========

rrlog is a pure Python logging tool. 
It is for both debugging and production and provides common features instantly. 
These are:

* Log Rotation
* Remote Logging
* Stacktrace logging (i.e. automatic call paths in logfiles)
* EMail notification
* logging into ASCII text files
* logging into a database
* Optional Integration with the python standard logging

**How it looks like, for the impatient**

A rotating server to log over sockets looks like::

	logServer = filewriter.createRotatingServer(
		filePathPattern = "./myfile-%s.log",
		rotateCount=3,
		rotateLineMin=10,
		)
	socketserver.startServer(logServer)
	

and an application using that server::

	log = socketclient.createClientLog(
		errorHandler="stderr",
		)
	log("Hello")


See below for full examples.


**Most battery types included**

Everything works instantly. No additional libraries required, except for database logging.
Database logging needs the `SqlAlchemy`_ package.

**Where it sucks**

* It is designed for and tested with a multi-process but not multithreaded application.
  Notice that nobody did care for a threaded environment yet. It *should* work threaded with remote logging.
  See :ref:`multithings`

**Major improvements likely to come next are:**

* The rotation is triggered by the number of logged messages only. A time/date-triggered rotation is missing
* only ASCII logging is specified. Unicode messages should become standard with Python3.


Basic usage
====================

Create a callable log object
--------------------------------
#. call a "create...()" function
        There are multiple conventient create() functions. Each makes a specific log configuration: for local or remote logging, into a file or a database etc.
        Look into the :ref:`basics` to see which create...() functions are available.
#. You got a log object. Call it with these arguments:

   * the log message (str)
   * an optional "category", which is a single character. That "category" rawly corresponds with the "info","debug","warn"... levels of the standard logging.

   Example::
   
      log("Uuups!","E")

Althought that log object is ready to use, you can :ref:`example_standardlogging`. (The log integrates as a handler.)

There are more arguments.
See  :ref:`basics` or the :py:meth:`rrlog.Log.__call__` docstring.



The category parameter
----------------------------

Categories are custom. They fit specific needs. 
However there is a convention: "E" for error messages, "W" for warnings.

The category latter appears in each logged line (leftmost, by default).  

Example use of the category: Messages with category "U" could trace the user behaviour of your website.
By extracting all logfile lines that start with "U ", you get a log essence with the user behaviour.
rrlog can also :ref:`example_email` for selected categories. 
For example, "S" could mark Security relevant messages which automatically trigger emails. 
Or, with every text a user typed into the contact formular, we log with category "M" and the user message as content. The rrlog can immediately send an email with the logged content.



*Now for something completely different ...*

.. _basics:

Basic Examples
=======================

.. toctree::
   :maxdepth: 1

   Simply Locally <ex_locally.rst>
   Remote with sockets <ex_sockets.rst>
   Remote with XMLRPC <ex_xmlrpc.rst>
   Use Pythons Standard Logging <ex_standard.rst>


.. _morefeatures:

More features
=======================

.. toctree::
   :maxdepth: 2

   morefeatures.rst
   

Remarks
=======================

.. toctree::
   :maxdepth: 2

   remarks.rst


.. _requirements:

Requirements
====================

When using database logging, the SQLAlchemy library is required. File logging needs no additional library.

Tested environment:

* CPython 2.7 on 64Bit Linux
* SQLAlchemy 0.8.1

Only this environment is tested.
rrlog supports a wide range of Python and SQLAlchemy versions, to minimize dependency trouble.
There's a wide version range expected to work:

* SQLAlchemy: all >= 0.3.2
* Python: from 2.7 to 3.4 (current)

If some of these "supported versions" don't work, it is considered a bug. Please tell (:ref:`contact`)


.. _contact:

Contact
================
Bug reports, improvements ...

Mail to rrlog at reifenberg.de

Or see http://www.reifenberg.de/rrlog/ or the `Github`_ site


License (MIT)
=======================

.. literalinclude:: ../../LICENSE.txt


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
