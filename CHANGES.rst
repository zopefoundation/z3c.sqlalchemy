Change log
==========

1.5.3 (2023-09-08)
------------------

- Fix transaction rollback with DBAPI cursor.execute.
  (`#17 <https://github.com/zopefoundation/z3c.sqlalchemy/issues/17>`_)


1.5.2 (2020-11-13)
------------------

- fix ``MANIFEST`` to include the change log


1.5.1 (2020-11-13)
------------------

- add linting to ``tox`` configuration and apply linting fixes

- fixed installation error in setup.py (release 1.5.0 is broken)


1.5.0 (2020-11-13)
------------------

- add support for Python 3.5-3.9

- Standardize namespace __init__

- Fix to work with zope.sqlalchemy 1.2

1.4.0 (2009-12-02)
------------------

- removed compatibility code with older Zope versions

- fixed import issue with modern zope.component versions

- fixed registering of custom mappers

1.3.11 (26.10.2009)
-------------------

- Don't create a new MetaData in LazyMapperCollection,
  but use the one created in the wrapper.
  In some cases, you could have some tables in the metadata created in the wrapper,
  and some tables in the metadata created in the LazyMapperCollection,
  which gave an error when trying to create relations.

- When generating the mapper class, make sure table.name is a string.
  It can be unicode when use_unicode=1 with MySQL engine.

1.3.10 (04.08.2009)
-------------------

 - removed SA deprecation warning

1.3.9 (06.01.2009)
------------------

 - made 'twophase' configurable

1.3.8 (06.01.2009)
------------------

 - replace asDict() with a dictish proxy implementation

1.3.7 (12.12.2008)
------------------

 - better support for SQLAlchemy declarative layer

1.3.6 (23.11.2008)
------------------

  - zip_safe=False

1.3.5 (05.09.2008)
------------------

  - restored compatibiltiy with SA 0.4.X

1.3.4 (04.09.2008)
------------------

  - added 'extension_options' parameter

1.3.2 (29.07.2008)
------------------

  - updated dependencies to latest zope.sqlalchemy release

1.3.1 (24.06.2008)
------------------

  - relaxed zope.* dependencies

1.3.0 (02.06.2008)
------------------

  - support for sqlalchemy.ext.declarative

1.2.0 (25.05.2008)
------------------

  - now using zope.sqlalchemy for ZODB transaction integration

  - internal class renaming

  - removed PythonBaseWrapper. Now there is only *one* ZopeWrappe class.

  - requires SQLAlchemy 0.4.6 or higher

  - requires zope.sqlalchemy 0.1 or higher

1.1.5 (08.05.2008)
------------------

  - better error handling in case of a rollback (patch by Dieter Maurer)

1.1.4 (15.03.2008)
------------------

  - reorganized .txt files

1.1.3 (20.02.2008)
-------------------

  - another savepoint fix

  - fixed regression error introduced by previous change: commit the
    zope transaction when ready in tpc_finish [maurits]

  - fixed issue where session's transaction.nested was being called as
    a callable (it should be straight attribute access) [Rocky]


1.1.2 (16.02.2008)
-------------------

  - fixed ZODB savepoint implementation. Now returning a proper dummy
    savepoint

1.1.1 (13.02.2008)
-------------------

  - the SessionDataManager now supports ZODB savepoints

1.1.0 (17.01.2008)
-------------------

  - WARNING: this version requires SA 0.4.X and higher 

  - fixed import issues with the upcoming SA 0.4.X series

  - create_session() calls (for SA 0.4.X)

  - the unittests support an optional $TEST_DSN environment in order
    to run the test against an existing database (other than SQLite)
               
  - major overhoul of the Zope transaction integration: now using
    one DataManager for the session object and the connection. The 
    connection as returned through the 'connection' property is also
    used for creating a new 'session'. Older z3c.sqlalchemy version
    used separate connections. This allows applications to use both
    a session and a connection within the same Zope request/thread
    without running into transaction problems. SQL actions and
    session related modifications should happen within the same
    transaction.

  - Wrapper constructor now accepts two new optional dicts 
    'engine_options' and 'session_options' that will be passed down 
    to the engine and the sessionmaker.  Patch provided by 
    Klaus Barthelmann.

  - mapped objects now provide a method asDict() to return the values 
    of an objects as dict.

 
1.0.11 (30.07.2007)
-------------------

  - replaced BoundMetaData() with MetaData() (requires SA 0.3.9+)

  - removed zope.* dependencies in order to avoid zope.* version
    mismatches for now


1.0.10 (16.07.2007)
-------------------

  - using Zope 3.3.X as a fixed depenceny 
 

1.0.9 (08.07.2007)
------------------

  - added namespace declarations

  - reST-ified documentation


1.0.8 (28.06.2007)
------------------

  - SessionDataManager: create a session transaction as late
    as possible and only if necessary in order to minimize deadlocks.
    So z3c.sqlalchemy won't create a transaction any more if there
    only SELECT operations within the current session.


1.0.7 (27.06.2007)
------------------

  - SessionDataManager: moved commit code from tpc_vote()
    to tpc_finish() (Thanks to Christian Theune for the hint)

1.0.6 (25.06.2007)
------------------

  - added 'namespace_packages' directive to setup.py

  - cache 'metadata' property

1.0.5 (13.06.2007)
------------------

  - It should be now safe to use sessions from multiple wrappers
    within one Zope transaction. In former versions of z3c.sqlalchemy
    calling wrapper1.session and wrapper2.session within the same
    transaction would return a session bound to wrapper1 in both
    cases.

1.0.4 (09.06.2007)
------------------

  - added new 'transactional' flag (used by SQLAlchemyDA only)

1.0.3 (26.05.2007)
------------------

   - new 'cascade' parameter for the Model.add()

   - tweaked the ZODB transaction integration a bit

1.0.2 (13.05.2007)
------------------

   - MappedClassBase has a new convinience method getMapper() that returns a
     mapper class associated through a relation with the current mapper


1.0.1 (unreleased)
------------------

   - MappedClassBase: new clone() method

   - more checks in Model.add()


1.0.0 (05.05.2007)
------------------

   - source code polishing
   
   - documentation update


0.1.13 (05.05.2007)
-------------------

   - sessions were returned from the wrong cache

   - moved the rollback/commit handling inside the SessionDataManager
     in order to play more nicely with the TPC. See
     http://mail.zope.org/pipermail/zodb-dev/2007-May/010996.html


0.1.12 (03.05.2007)
-------------------

   - createSAWrapper() got a new optional 'name' parameter in order
     to register the wrapper automatically instead of using a dedicated
     registerSAWrapper(wrapper, name) call

0.1.11 (02.05.2007)
-------------------

   - added check for the 'mapper_class' attribute (classes from now
     on must be a subclass of MapperClassBase)

   - a Zope-aware SAWrapper now has a 'connection' property that can
     be used to execute SQL statements directly. 'connection' is an 
     instance of sqlalchemy.Connection and directly tied to the current
     Zope transaction.

   - changed the caching of the connection and session object for Zope wrapper
     since the id of a transaction is not reliable (different transaction
     object can re-use the same memory address leading to cache errors)


0.1.10 (30.04.2007)
-------------------

   - fixed a bug in mapper (unfortunately I forgot to commit a
     necessary change)

   - removed the 'primary_key' parameter introduced in 0.1.9 because
     we don't need. It can be defined within the model using a
     PrimaryKeyConstraint()

   - createSAWrapper: setting forZope=True for a non-postgres DSN
     now also returns a Zope-aware wrapper instance (instead
     of a BaseWrapper instance).  (Reported by Martin Aspeli)


0.1.9 (26.04.2007)
------------------

   - base.py: the 'model' parameter can now also be a callable
     returning an instance of model.Model

   - base.py: calling a model provider or a method providing a
     model with a BoundMetaData instance in order to allow 
     table auto-loading

   - Model.add() got a new parameter 'primary_key' in order to specify a
     primary_key hint. This is useful when you are trying to auto-load a view
     as Table() having no primary key information. The 'primary_key' parameter is
     either None or a sequence of column names.


0.1.8 (23.04.2007)
------------------

   - added shorter method names as aliases 

   - don't generate a new mapper class if a custom mapper
     class is defined within the model


0.1.7 (21.04.2007)
------------------

   - replaced 'echo' parameter of the constructor with a generic keyword
     parameter in order to provide full parameter support for
     create_engine. Optional arguments passed to the constructur are
     passed directly to create_engine()

   - fixed the documentation a bit

   - added registerMapper() to BaseWrapper class

   - registerSQLAlchemyWrapper() now defers the registration until
     the Wrapper is used first when calling getSQLAlchemyWrapper() 

   - the 'name' parameter of Model.add() now supports schemas (if
     available). E.g. when using Postgres you can reference as
     table within a different schema through '<schema>.<tablename>'.

   - Model.add() accepts a new optional parameter 'table_name' that
     can be used to specify the name of a table (including schema
     information) when you want to use the 'name' parameter as
     an alias for the related table/mapper.

 
0.1.6 (28.03.2007)
------------------

   - fixed a bug in registerSQLAlchemyWrapper

0.1.5 (28.03.2007)
------------------
  
   - registerSQLAlchemyWrapper() should now work with Zope 2.8-2.10

   - abort() was defined twice inside the DataManager class
 
0.1.4 (21.03.2007)
------------------

   - the Model class now behave (where needed) as a sorted
     dictionary. Its items() method must returned all items
     in insertion order.

0.1.3 (20.03.2007)
------------------

   - added getMappers() convenience method

   - the Zope wrapper uses SessionTransactions in order to be able
     to flush() as session with a transaction in order to read
     row previously inserted within the same transaction


0.1.2 (unreleased)
------------------

   - fixed class hierarchy issues with Postgres wrapper classes


0.1.1 (unreleased)
------------------

   - fixed setup.py

0.1 (18.03.2007)
----------------

   - initial version
