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
DB Writing via SQLAlchemy (SA).
@author: Ruben Reifenberg
"""

import warnings
from sqlalchemy import create_engine,MetaData,Column,Table,Integer,String
import rrlog
from rrlog import environment
from rrlog import server

MYSQL_ENGINE = "MyISAM"


def createRotatingServer(engineStr, rotateCount, rotateLineMin, tableNamePattern="log_%s", tsFormat=None, filters=None, observers=None, logwriterFactory=None, drop=True, cols=None, format_dict=None):
	"""
	:param engineStr: SQLAlchemy engine str
	:param tableNamePattern: table name incl.placeholder for int (rotate number), e.g. "mylog%d"
	:param filters: default = () See L{rrlog.server.LogServer.__init__}
	:param observers: default = () See L{rrlog.server.LogServer.__init__}
	:param tsFormat: timestamp format. See L{rrlog.server.LogServer.__init__}
	:param rotateCount: int >=1, how many tables to use for rotation
	:param rotateLineMin: rotate when ~ lines are written. None to switch off rotation.
	:param logwriterFactory: Creates LogWriter instances (one per db table). If None, the module variable LOGWRITER_CLASS is used.
	:param drop: if True, drop an eventually existing table. When False, append to an existing one (this is possible with rotateCount==1 only).
	:raises AssertionError: when drop==False and rotateCount > 1
	:param cols: Custom column configuration. See L{rrlog.server.dbwriter_sa.DBConfig.__init__}
	:param format_dict: callable taking a job and returning {colname:fieldcontent}. Ignored if a logwriterFactory is given.
	"""
	assert rotateCount >= 1, "rotate count is %s but can't be <1."%(rotateCount)
	assert drop==True or rotateCount==1, "rotate count cannot be >1 when drop is False"
	
	if logwriterFactory is None:
		logwriterFactory = lambda *args,**kwargs:LOGWRITER_CLASS(format_dict=format_dict,*args,**kwargs)
	elif format_dict is not None:
		warnings.warn("format_dict is ignored since logwriterFactory is already specified")
		
	return server.LogServer(
		writer = server.RotateLogWriter(
			getNextWriter=server.RotateWriterFactory(
				configs=[DBConfig(
					engineStr = engineStr,
					tablename=tableNamePattern%(i),
					drop=drop,
					cols=cols,
					)
					for i in range(0,rotateCount)
					],
				writerFactory=logwriterFactory,
				).nextWriter,
			rotateLineMin=rotateLineMin,
			),
		filters = filters,
		observers = observers,
		tsFormat = tsFormat,
		)


def createLocalLog(
	engineStr,
	rotateCount,
	rotateLineMin,
	traceOffset=0,
	tableNamePattern="log_%s",
	filters=None,
	observers=None,
	tsFormat="std1",
	stackMax=5,
	drop=True,
	catsEnable=None,
	catsDisable=None,
	seFilesExclude=None,
	name=None,
	cols=None,
	extractStack=True,
	):
	"""
	:param catsEnable: see L{rrlog.Log.__init__}
	:param catsDisable: see L{rrlog.Log.__init__}
	:param seFilesExclude: see L{rrlog.Log.__init__}
	:param filters: see L{rrlog.server.LogServer.__init__}
	:param observers: see L{rrlog.server.LogServer.__init__}
	:param tsFormat: timestamp format. See L{rrlog.server.LogServer.__init__}
	:param tableNamePattern: table name incl.placeholder for int (rotate number), e.g. "mylog%d"
	:param rotateCount: int >>1, how many tables to use for rotation
	:param rotateLineMin: rotate when ~ lines are written. None to switch off rotation.
	:param stackMax: see L{rrlog.Log.__init__}, default: 5 (==log 5 stack levels.)
	:param drop: if True, drop an eventually existing table. When False, append to an existing one (this is possible with rotateCount==1 only).
	:param extractStack: see L{rrlog.Log.__init__}
	:param cols: Custom column configuration. See L{rrlog.server.dbwriter_sa.DBConfig.__init__}
	:returns: callable log object, ready to use
	"""
	return rrlog.Log(
		server = createRotatingServer(
			engineStr,
			rotateCount,
			rotateLineMin,
			tableNamePattern,
			tsFormat=tsFormat,
			filters=filters,
			observers=observers,
			drop=drop,
			cols=cols,
			),
		traceOffset=traceOffset,
		stackMax=stackMax,
		catsEnable=catsEnable,
		catsDisable=catsDisable,
		seFilesExclude=seFilesExclude,
		name=name,
		extractStack=extractStack,
		)


def default_format_dict(job):
	"""
	Format the row fields for writing.
	:returns: {colname:fieldcontent} as to be written into the database row.
	"""
	return dict(
		pid=job.pid,
		threadname = job.threadname,
		msgid = job.msgid,
		msg = job.msg,
		cat = job.cat,
		ts = job.ts,
		cfunc=job.cfunc,
		cfn = job.cfn(),
		cln = job.cln(),
		path = job.pathStr(0), # 0 since v0.1.5. Was 1 with <=v0.1.4 to omit the cfn/cln in the path string.
		)


class _Coltypes(object):
	"""
	Column types
	"""
	Integer = Integer
	String = String


class DBConfig(_Coltypes):

	COLS_DEFAULT = (
			("pid", _Coltypes.Integer ),
			("threadname", _Coltypes.String(32) ), # how long? "By default, a unique name is constructed of the form "Thread-N" where N is a small decimal number"
			("msgid", _Coltypes.Integer ),
			("ts", _Coltypes.String(32) ),
			("cat", _Coltypes.String(1) ),
			("msg", _Coltypes.String(512) ),
			("cfunc", _Coltypes.String(32) ),
			("cfn", _Coltypes.String(32) ),
			("cln", _Coltypes.Integer ),
			("path", _Coltypes.String(512) ),
			)

	
	def __init__(self, engineStr, tablename, drop=True, cols=None):
		"""
		:param engineStr: SQLAlchemy engine str
		:param tablename: str
		:param drop: If False, an eventually existing table is not deleted but extended. Only true makes sense with rotation.
		:param cols: All log table column names and types.
		
			default=None. If None, the DBConfig.COLS_DEFAULT is used.		
				
			Use the COLS_DEFAULT as a base for you own column configuration.
			This is a 3-tuple of (col-name:str,col-type,kwargs:dict) where:
			col-name is the desired DB column. This name can be used as kwarg in the log() calls
			col-type is DBConfig.Integer or DBConfig.String
			kwargs (optional) is for the sqlalchemy Column.
			
			Example:
			To add an own integer column, take the default columns, and add your
			own pair of (column-name,column-type) like that:
			cols=DBConfig.COLS_DEFAULT + (("mycolumn",DBConfig.Integer))
			To define you column as primary key, use
			cols=DBConfig.COLS_DEFAULT + (("mycolumn",DBConfig.Integer,{"primary_key":True}))
		"""
		self.drop = drop
		self.engineStr = engineStr
		self.tablename = tablename
		if cols is None: cols = self.__class__.COLS_DEFAULT
		self.cols = cols


class DBLogWriter(object):
	"""
	USes SQLAlchemy (sa),
	Assigned to 1 Table
	"""
	def __init__(self, config, format_dict=None):
		"""
		:param config: DBConfig
		"""
		db = create_engine(config.engineStr,echo=False)

		if environment.sa_v0_3_x:
			from sqlalchemy import BoundMetaData
			metadata = BoundMetaData(db)
		else:
			metadata = MetaData(db)

		self._table = Table( config.tablename, metadata,
			Column("id", Integer, primary_key=True),
			mysql_engine=MYSQL_ENGINE,
			*self.createColumns(colsConfig=config.cols)
			)

		if config.drop:
			metadata.drop_all()
		metadata.create_all()

		self._insert = self._table.insert()
		# the compile() optimization is considered erroneous with SA 0.6
		# See Ticket #1806: .execution_options(compiled_cache={}) is suggested instead
		# Anyway, can't measure a remarkable speed diff (with both compile and execution_options),
		# We omit the latter (and stick with compile() just for not touching old behavior.)
		if environment.sa_lt_v0_6_0:
			self._insert = self._insert.compile()

		self._lineCount = 0
		if format_dict is not None:
			self._format_dict=(format_dict,)
		else:
			self._format_dict=(self._format_dict,)


	def _format_dict(self, job):
		"""
		Default formatting method.
		
		:rtype: {}
		:returns: {colname:fieldcontent} for a single row
		"""
		res = default_format_dict(job)
		res.update(job.special)
		return res


	def createColumns(colsConfig):
		"""
		There is no primary key column; these are content columns only.
		
		:returns: [] of SQLAlchemy Column that make up my log table
		:param colsConfig: (col-name:str,col-type,kwargs:dict) where
		
			col-type is DBConfig.Integer or DBConfig.String
			kwargs is optional and contains kwargs for Column() of sqlalchemy
			example: ("ipadress",DBConfig.String,{"default":"127.0.0.1"})
		"""
		res = []
		try:
			for x in colsConfig:
				assert len(x) in (2,3)
				if len(x) == 3:
					kwargs = x[2]
				else:
					kwargs = {}
				res.append( Column(x[0],x[1],**kwargs) )
		except Exception as e:
			print("colsConfig was:%s"%(str(colsConfig)))
			raise
		return res
	createColumns = staticmethod(createColumns)


	def estimateLineCount(self):
		"""
		For performance reasons, it is allowed to estimate instead count exactly.
		(Remark: This implementation is working exactly.)
		
		:returns: count of already written lines
		"""
		return self._lineCount


	def getTable(self):
		"""
		:rtype: SQLAlchemy Table
		"""
		return self._table
	
	
	def close(self):
		pass


	def writeNow(self, job):
		"""
		Write without buffering, return when written
		"""
		self._insert.execute(
			self._format_dict[0](job)
			#**job.getFormattedDict()
			)
		self._lineCount += 1

LOGWRITER_CLASS = DBLogWriter
