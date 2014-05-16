More Features
**********************


*A Remote Rotating Log for Python that works instantly*


.. _feature_stacktrace:

Stack Path logging
==========================

Log the stack path along with each message. 
This is a debugging feature.

Note: That stack path is intended to be human readable, as a debugging information.

**How long ?**

* The create... functions take a stackMax parameter to limit the logged stack length.
* When remote logging, these parameters are found in the client side create... function.
* See also the extractStack parameter to completely switch off stack extraction (for performance reasons).

→ :class:`rrlog.Log` for these parameters. 

**Into a database**

* Column: The callers path is written into the "path" column.
* The top element of the path is written redundantly in the cfn/cln columns
  ("Callers File Name" resp. "Callers Line Number").
  Thus, cfn and cln can be evaluated immediately (without parsing the path string).

Unwanted elements of the path can be skipped, for better readability.
→ :ref:`example_reducestackpath`
    
    


.. _example_reducestackpath:

Shorten stack paths
=====================

To hide unwanted parts of the stack trace, initialize :py:class:`rrlog.Log` with one of these parameters:

* seFilesExclude : a callable telling which parts to skip in the stack path. 
  
* traceOffset : skips the first components of the stacktrace. We need to know (or to try out) how many to skip.
  traceOffset is preferrable when we have an own wrapper around the log object.
  Increase it to 1, to hide exactly the first method call, and so on. 


For the use case of :ref:`example_standardlogging`, both ways work.
We prefer the seFilesExclude way.
We don't need to bother the amount of calls that happen inside the logging library, and there is already a predefined :py:func:`rrlog.logging23.seFilesExclude` specially for the "standard logging" case:  


.. literalinclude:: ../demo/demo_logginghandler.py
   :lines: 42-55

All the "logging.__init__" stuff is removed now.


Time Stamp format
=======================

Custom time stamp formats are possible.
The create... functions take a tsFormat parameter; for a description, see :py:class:`rrlog.server.LogServer` 
When remote logging, this parameter is found in the server side create... function.


.. _example_formatting:

Custom line format
===============================

.. literalinclude:: ../demo/demo_customlinefiles.py
   :lines: 42-
   
   
Another example for database logging:

.. literalinclude:: ../demo/demo_customlinedatabase.py
   :lines: 42-
   
Each formatter method can use the attributes of the :py:class:`rrlog.server.MsgJob` to build a line.
A custom formatter method can optinally use :ref:`adhoc_parameters` 


.. _adhoc_parameters:

Custom parameters
===========================

The log call can take custom named parameters.
These appear in the resulting Job. A custom line formatting method can put these parameters in the logged line. 
→  "special" parameter in :py:meth:`rrlog.Log.__call__`


Don't rotate
====================

The 'Standard Case' is defined to be rotation, along with overwriting of old files/tables.

To disable, set rotateLineMin=None in the create* functions. Rotation is switched off, and the file/table is appended forever.
In addition, the rotateCount parameter must be set to 1.


.. _example_indent:

Indent lines
========================

to visualize a call hierarchy:

There's a filter available that indents each line, depending on how deep in the stack we are.

→ :mod:`rrlog.contrib.stackindent`
 
The filter could be applied with Database logging, too. But surely, it looks best with files or standard out.

Example with standard out:

.. literalinclude:: ../demo/demo_indentstdout.py
   :lines: 42-

Note: The filter is applied inside the convenient create function
 :func:`rrlog.contrib.stackindent.createPrintIndentLog`

Same example with files:

.. literalinclude:: ../demo/demo_indentfiles.py
   :lines: 42-


Observe and filter
===========================================

Messages can trigger actions, and can be manipulated before they are written.
Our terminology is:

* "observers" read messages *after* they are written, and eventually trigger an action
* "filters" are similar, except: they are called *before* the message is written, and they can manipulate the job object - especially the message text.

A predefined observer available is :ref:`example_email` that sends mails for defined message categories.

A predefined filter available is the function that formats each line (see also :ref:`example_formatting`), or the optional line indention (:ref:`example_indent`).

Filters and observers can be added n the create... functions. With remote logging, they are at server side.
→ :py:meth:`rrlog.LogServer.__init__` for more documentation of these parameters. 



On / Off
==================

There are on / off methods in :class:`rrlog.Log` to disable / enable that log instance.


   
.. _example_email:

Send mails
========================

The log can send lovely letters when messages of selected categories (like "E" for error) appear.

The messages are collected for a (configurable) "collect time" and sent bundled.
We can send important stuff quickly, otherwise collect messages for a while.

Create a mail notifier ...

.. literalinclude:: ../demo/demo_smtpmail.py
   :lines: 42-65
   
   
... and hook it as "observer" into the log.
That notifier sends mails when messages of the given categories are logged.

.. literalinclude:: ../demo/demo_smtpmail.py
   :lines: 68-

**Independent line formatting in mails**
The :py:func:`rrlog.contrib.mail.mailnotifier` takes an own format_line parameter, independently from the formatting in the log files.

**Custom mail protocols**   
There is a simple SMTP mailer: :py:class:`rrlog.contrib.mail.SMTPMailer` already included.
For other mail protocols (e.g. SMTP authentication with starttls, or a sendmail server),
you need to extend or replace it. 

**! Missing overflow protection**
There is no limit to protect us from very long mails yet.


→  module: :py:mod:`rrlog.contrib.mail`