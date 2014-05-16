Examples for rrlog
********************************


*A Remote Rotating Log for Python that works instantly*


Simply locally
================

Into stdout
------------

Log into standard out:

.. literalinclude:: ../demo/demo_stdout.py
   :lines: 42-

→  :py:mod:`rrlog.server.printwriter`



Into files
------------

Log rotating into 3 files, each with 10 lines max. (existing files in the working directory are overwritten)

.. literalinclude:: ../demo/demo_files.py
   :lines: 42-

→  :py:mod:`rrlog.server.filewriter`


Into database tables
---------------------

Log rotating into 3 tables, each with 10 lines max. (existing tables are overwritten)

.. literalinclude:: ../demo/demo_database.py
   :lines: 42-

→  :py:mod:`rrlog.server.printwriter`

→  :py:mod:`rrlog.server.dbwriter_sa`
