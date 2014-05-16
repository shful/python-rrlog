Examples for rrlog
********************************


*A Remote Rotating Log for Python that works instantly*


.. _example_standardlogging:

Use Pythons standard logging
===================================

The log object (the callable thing we always used above) can be registered as a handler:

.. literalinclude:: ../demo/demo_logginghandler.py
   :lines: 60-

→  :py:func:`rrlog.logging23.handler`

Now you can use the usual python logging calls.

**Beautify Stacktraces**

Logged stack traces look ugly with the python standard logging. 
The __init__ file of the standard logging package dominates somewhat. It can be hidden.

→  :ref:`example_reducestackpath`


**What with the custom categories ?**

A drawback of the standard logging module: We can't use custom message categories
(On the other hand, standard logging allows to register separate handlers.)

As a workaround, rrlog interprets the LEVELs of standard logging as category letters.
For example, the call logging.error(...) automatically gets category "E".
The mapping of LEVEL<->category is in a LEVELMAP in :py:mod:`rrlog.logging23. You may customize that map.
