Examples for rrlog
********************************


*A Remote Rotating Log for Python that works instantly*




Remote with sockets
=========================

This is the preferred way to log remotely.
It is also the right way for processes logging to the same file (with a server remotely, or on the same machine). 

**(Re-)Connection behavior**

Any log client connects the log server everytime the server is available. 
**While a log server is down, messages are lost silently.**
When the server was down (or unreachable) and is up again, all clients start to use the server again.  

**Host and Ports**

By default, the connection uses "localhost" and a default port → :py:data:`rrlog.globalconst.DEFAULTPORT_SOCKET`

You can specify a list of allowed ports on both sides.
The server will listen on the first port that is available.
The client logs to the first port where a server is found.  



A socket server for stdout
----------------------------


.. literalinclude:: ../demo/demo_socketserverstdout.py
   :lines: 42-

→  :py:mod:`rrlog.server.socketserver`

→  :py:mod:`rrlog.server.printwriter`


A socket server for files
------------------------------

.. literalinclude:: ../demo/demo_socketserverfiles.py
   :lines: 42-

→  :py:mod:`rrlog.server.socketserver`

→  :py:mod:`rrlog.server.filewriter`


A socket server for database tables
---------------------------------------

.. literalinclude:: ../demo/demo_socketserverdatabase.py
   :lines: 42-

→  :py:mod:`rrlog.server.socketserver`

→  :py:mod:`rrlog.server.dbwriter_sa`





A socket client in your application
--------------------------------------

.. literalinclude:: ../demo/demo_socketclient.py
   :lines: 42-

→  :py:mod:`rrlog.socketclient`

