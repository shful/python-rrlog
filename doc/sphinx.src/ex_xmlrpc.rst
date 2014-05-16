Examples for rrlog
********************************


*A Remote Rotating Log for Python that works instantly*



Remote with xmlrpc
====================

Remote logging is intended to log on a remote machine. Or, which might be a very common use, to log from multiple processes on the same machine into one logfile/table.

This requires two create* calls. One makes the log server, one makes the client in your application.
Most parameters are now found in the server create* function, e.g. the rotation configuration.

**Host and Ports**

.. todo:module-level variables not auto-documented :-(
By default, the connection uses "localhost" and a default port → :py:data:`rrlog.globalconst.DEFAULTPORT_XMLRPC`

You can specify 1..n ports on both sides. The server uses the first free port. The client uses the first port where a server seems available.  



An XMLRPC server for stdout
----------------------------


.. literalinclude:: ../demo/demo_xmlrpcserverstdout.py
   :lines: 42-

→  :py:mod:`rrlog.server.xmlrpc`

→  :py:mod:`rrlog.server.printwriter`


An XMLRPC server for files
------------------------------

.. literalinclude:: ../demo/demo_xmlrpcserverfiles.py
   :lines: 42-

→  :py:mod:`rrlog.server.xmlrpc`

→  :py:mod:`rrlog.server.filewriter`


An XMLRPC server for database tables
---------------------------------------

.. literalinclude:: ../demo/demo_xmlrpcserverdatabase.py
   :lines: 42-

→  :py:mod:`rrlog.server.xmlrpc`

→  :py:mod:`rrlog.server.dbwriter_sa`


An XMLRPC client in your application
--------------------------------------

.. literalinclude:: ../demo/demo_xmlrpcclient.py
   :lines: 42-

→  :py:mod:`rrlog.xmlrpc`


Care for the correct server running ! For example, a socket server erroneously waiting on that port can cause the XMLRPC Client to block stupidly and wait without any Error message.
