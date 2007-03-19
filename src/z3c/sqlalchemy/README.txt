##########################################################################
# z3c.sqlalchemy - A SQLAlchemy wrapper for Python/Zope
#
# (C) Zope Corporation and Contributors
#
# Written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
# and ZOPYX Ltd. & Co. KG, Tuebingen, Germany
#
# z3c.sqlalchemy is published under the Zope Public License V 2.1
##########################################################################


What is z3c.sqlalchemy?
======================

z3c.sqlalchemy is yet another wrapper around SQLAlchemy. The functionality of
the wrapper is basically focused on easy integration with Zope 2 and Zope 3.
The wrapper cares about connection handling, optional transaction integration
with Zope 2/3 and wrapper management (caching, introspection). z3c.sqlalchemy
gives you flexibe control over the mapper creation. Mapper classes can be

    - auto-generated (with or without autodetection of table relationships)

    - configured by the developer 


Requirements:

    - Zope 2.8+, Zope 3.X

    - SQLAlchemy    


Usage
=====

Basic usage from within a pure Python application:

   > from haufe.sqlalchemy import createSQLAlchemyWrapper
   > wrapper = createSQLAlchemyWrapper('postgres://postgres:postgres@host/someDB')
   > session = wrapper.session
   > FormatMapper = wrapper.getMapper('format') # auto-generated mapper for table 'format'
   > for row in session.query(FormatMapper).select(...): print row
   > session.flush() # if necessary

When using Zope 2/3 you can use the same code but you want a wrapper that
participates in Zope transactions. For this purpose you must use the additional
parameter 'forZope':

   > from haufe.sqlalchemy import createSQLAlchemyWrapper
   > wrapper = createSQLAlchemyWrapper('postgres://postgres:postgres@host/someDB', forZope=True)
   > session = wrapper.session

In this case the session will participate automatically in a Zope transaction.
The wrapper will call automatically session.flush() upon a transaction commit.
Please note that 'wrapper.session' will always return the same session instance
within the same transaction and same thread.

For a real-world application you don't want to create a new wrapper for every
new request.  Instead you want to register a wrapper instance as named utility
(ISQLAlchemyWrapper) and lookup up the wrapper (the utility!) by name from
within your application. This approach is very similiar to looking up an
databases adapter or a ZSQL method through acquisition.
   

By default "wrapper.getMapper(name)" will always auto-generate a new mapper
class by using SQLAlchemy auto-load feature. The drawback of this approach is
that the mapper class does not know about relationships to other tables. Assume
we have a one-to-many relationship between table A and B and you want
z3c.sqlalchemy to generate a mapper that is aware of this relationship. For
this purpose you can create a wrapper with a "model" as optional parameter. A
model is basically a configuration or a series of hints in order to tell
z3c.sqlalchemy how mappers a generated.

Example:

   > from haufe.sqlalchemy import createSQLAlchemyWrapper, Model
   > model = Model()
   > model.add(name='A', relations=('B',))
   > wrapper = createSQLAlchemyWrapper('postgres://postgres:postgres@host/someDB', model=model)
   > AMapper= wrapper.getMapper('A') 

This will generate a mapper AMapper where all instances of AMapper have a
property 'B' that relates to all corresponding rows in B (see the SQLAlchemy
documentation on mappers, properties and relation()). In this example you
define the relationship between A and B explictly through the 'relations'
parameter (as a sequence of related table names).

z3c.sqlalchemy also supports the auto-detection of relationships between tables.
Unfortunately SQLAlchemy does not support this feature out-of-the-box and in a portable
way. Therefore this feature of z3c.sqlalchemy is highly experimental and currently
only available for Postgres (tested with Postgres 8.X).

   > from haufe.sqlalchemy import createSQLAlchemyWrapper, Model
   > model = Model()
   > model.add(name='A', autodetect_relations=True)
   > wrapper = createSQLAlchemyWrapper('postgres://postgres:postgres@host/someDB', model=model)
   > AMapper= wrapper.getMapper('A') 

In this case z3c.sqlalchemy will scan all tables in order to detect
relationships automatically and build the mapper class and its properties
according to the found relationships. Warning: this feature is experimental and
it might take some time to scan all tables before the first request. Currently
only Postgres tables in the 'public' schema are supported).

In same cases you might be interested to use your own base classes for a
generated mapper.  Also this usecase is supported by passing the base class to
the model using the 'mapper_class' parameter:

   > from haufe.sqlalchemy import createSQLAlchemyWrapper, Model
   > class MyAMapper(object): pass
   > model = Model()
   > model.add(name='A', relations=('B',) mapper_class = MyAMapper)
   > wrapper = createSQLAlchemyWrapper('postgres://postgres:postgres@host/someDB', model=model)
   > AMapper= wrapper.getMapper('A')  # AMapper will be an instance of MyAMapper


Supported systems
=================
z3c.sqlalchemy was developed with Zope 2.8/Zope 3.0 and basically tested against
Postgres 8.X and SQLite 3.3.


Author
======
z3c.sqlalchemy was written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
and ZOPYX Ltd. & Co. KG, Tuebingen, Germany.


License
=======
z3c.sqlalchemy is licensed under the Zope Public License 2.1. 
See LICENSE.txt.


Contact
=======
Andreas Jung, 
E-mail: info at zopyx dot com
Web: http://www.zopyx.com


Credits
=======
Parts of the code are influenced by z3c.zalchemy (Juergen Kartnaller, Michael
Bernstein & others) and Alchemist (Kapil Thangavelu)


