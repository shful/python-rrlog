

Remarks
******************


*A Remote Rotating Log for Python that works instantly*


.. _multithings:

Multiprocess & Multithread
========================================

The log is designed with multiple processes in mind, but not multiple threads.
(The website it was made for uses processes and no threading.)
*Consider the log as untested in multithreaded applications.*

**Still log with multithreading ?**

Without remote logging, each process or thread must write a separate file (or DB table).

(While is not generally impossible to write one file with multiple processes, 
this may fail occasionally - depending on your operating system. Database tables do a better job in this respect. 
Anyway, the rotation control is not thread safe.)

Maintaining a separate log file per thread would require a separate log object per thread. Usually not desired.
Better use remote logging, preferably with the fast socket module. 
That allows rotation, and handling concurrent write access is up to the log server.


Security of remote logging
=============================

You can provide **multiple ports** for server and client(s). 
This is nice in development (the feature addresses the problem that sometimes ports are blocked until timeout). 
In production, I'd prefer a single port for best control over the connections going on.

**XMLRPC** is re-using HTTP, which is tolerated by most firewalls. That can be a security issue.
With an XMLRPC logging server, it is a good idea to double check it has HTTP access only from the right addresses.

A potential risk has always been the **deserialize routines** of a server. 
Pythons core (c)Pickle module is known to be vulnerable by malicous data. 
rrlog instead uses the json serializer by default for remote logging 
(thats why Python2.3 legacy support was skipped.) 
See the :py:class:`rrlog.xmlrpc` module if you want to replace the xmlrpc serializer, e.g. marshal,cerealizer,pickle...


Performance
==================

Database logging
-----------------------------

Logging into a database is slower than logging into plain files.

*A simple benchmark*

rrlog (pure, without the Python logging framework) writes 10000 messages, each of 20 ASCII characters plus an increasing number, on an old Single Core Desktop PC.

* Files are plain text files on the local hard disk. The rrlog flushes the file after each line.
* As a comparison, a MySQL5/MyISAM database is written. SQLALchemy is v0.4.2.

Times are: Files: 0.35 sec, database: 4.4 sec.

The times increase linear as expected (5000 messages take half the time.) Most time is taken on database side. 
An SQLite memory-only database (which is somewhat unusual for a log) takes half the time of MySQL.

I'd roughly estimate database logging is about 10 times slower than text file logging.
Direct logging into a database is fine for easy analyse, search, sort and selective-backup. When the speed is good enough, I'd consider that way.  

XMLRPC remote logging
---------------------------

When measuring with a the desktop single core desktop PC -- 
 Log Server and Client on the same machine -- XMLRPC logging is about 15-25 times slower than non-remote logging.
 
For productive use with high traffic, use the pure socket version (or non-remote logging into files if possible).

Stacktrace extraction
------------------------
Another slowdown feature is the stacktrace logging. 
This is intended for debugging and development. It can slow down logging about 2-3 times, depending on the max size of the stacktraces.

For best performance, completely switch it off (see :ref:`feature_stacktrace`)
  