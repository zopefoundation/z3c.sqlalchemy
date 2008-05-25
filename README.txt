=====================================================
z3c.sqlalchemy - A SQLAlchemy wrapper for Python/Zope
=====================================================


What is z3c.sqlalchemy?
=======================

z3c.sqlalchemy is yet another wrapper around SQLAlchemy. The functionality of
the wrapper is basically focused on easy integration with Zope 2 and Zope 3.
The wrapper cares about connection handling, optional transaction integration
with Zope 2/3 and wrapper management (caching, introspection). z3c.sqlalchemy
gives you flexible control over the mapper creation. Mapper classes can be

- auto-generated (with or without autodetection of table relationships)
- configured by the developer 


What z3c.sqlalchemy does not do and won't do:
=============================================

- no support for Zope 3 schemas 
- no support for Archetypes schemas

z3c.sqlachemy just tries to provide you with the basic functionalities you need
to write SQLAlchemy-based applications with Zope 2/3. Higher-level
functionalities like integration with Archetypes/Zope 3 schemas are subject to
higher-level frameworks.  z3c.sqlalchemy does not address these frameworks.


Requirements:
=============

- Zope 2.8+, Zope 3.X
- SQLAlchemy 0.4.6 or higher  (no support for SQLAlchemy 0.3) 
- zope.sqlalchemy 0.1.0 or higher
- Python 2.4+


Installation:
=============

Either using easy_install::

  easy_install z3c.sqlalchemy

or using Python directly::

  python2.4 setup.py install

Note:
-----
z3c.sqlalchemy depends on the modules **zope.component**, **zope.schema**
and **zope.interface**. If you are using z3c.sqlalchemy in a Python-only
environment, ensure the these components have to be installed either
as eggs or by setting the PYTHONPATH to a corresponding Zope 2 
or Zope 3 installation.


Usage
=====

Basic usage: 

   from z3c.sqlalchemy import createSAWrapper
   wrapper = createSAWrapper('postgres://postgres:postgres@host/someDB')
   session = wrapper.session
   FormatMapper = wrapper.getMapper('format') # auto-generated mapper for table 'format'
   for row in session.query(FormatMapper).select(...): print row
   session.flush() # if necessary

The session will participate automatically in a Zope transaction.  The wrapper
will call automatically session.flush() upon a transaction commit.  Please note
that 'wrapper.session' will always return the same session instance within the
same transaction and same thread.

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

Example::

   from z3c.sqlalchemy import createSAWrapper, Model
   model = Model()
   model.add(name='A', relations=('B',))
   wrapper = createSAWrapper('postgres://postgres:postgres@host/someDB', model=model)
   AMapper= wrapper.getMapper('A') 

This will generate a mapper AMapper where all instances of AMapper have a
property 'B' that relates to all corresponding rows in B (see the SQLAlchemy
documentation on mappers, properties and relation()). In this example you
define the relationship between A and B explictly through the 'relations'
parameter (as a sequence of related table names).

z3c.sqlalchemy also supports the auto-detection of relationships between tables.
Unfortunately SQLAlchemy does not support this feature out-of-the-box and in a portable
way. Therefore this feature of z3c.sqlalchemy is highly experimental and currently
only available for Postgres (tested with Postgres 8.X).::

   from z3c.sqlalchemy import createSAWrapper, Model
   model = Model()
   model.add(name='A', autodetect_relations=True)
   wrapper = createSAWrapper('postgres://postgres:postgres@host/someDB', model=model)
   AMapper= wrapper.getMapper('A') 

In this case z3c.sqlalchemy will scan all tables in order to detect
relationships automatically and build the mapper class and its properties
according to the found relationships. Warning: this feature is experimental and
it might take some time to scan all tables before the first request. Currently
only Postgres tables in the 'public' schema are supported).

In same cases you might be interested to use your own base classes for a
generated mapper.  Also this usecase is supported by passing the base class to
the model using the 'mapper_class' parameter::

   from z3c.sqlalchemy import createSAWrapper, Model
   from z3c.sqlalchemy.mapper import MappedClassBase
   class MyAMapper(MappedClassBase): pass
   model = Model()
   model.add(name='A', relations=('B',) mapper_class = MyAMapper)
   wrapper = createSAWrapper('postgres://postgres:postgres@host/someDB', model=model)
   AMapper= wrapper.getMapper('A')  # AMapper will be an instance of MyAMapper

When you are working with wrapper in a Zope 2/3 environment you are usually
interested to to register a wrapper instance as named utility implementing
ISQLAlchemyWrapper. You can can perform the registration lazily by passing the
name utility as 'name' parameter to the createSAWrapper(...,
name='my.postgres.test.db') method.

A convenience method for obtaining a wrapper instance by name is available
through getSAWrapper::

    createSAWrapper(dsn,..., name='my.name')
    ...
    wrapper = getSAWrapper('my.name')


Supported systems
=================

z3c.sqlalchemy was developed with Zope 2.8/Zope 3.0 and basically tested against
Postgres 7.4.X and 8.X and SQLite 3.3.


Known issues
============

Running z3c.sqalchemy against MySQL databases without transaction support might
cause trouble upon the implicit commit() operation. For this reason MySQL without
transaction support isn't supported right now


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

| ZOPYX Ltd. & Co. KG
| Andreas Jung
| Charlottenstr. 37/1
| D-72070 Tuebingen, Germany 
| E-mail: info at zopyx dot com
| Web: http://www.zopyx.com


Credits
=======

Parts of the code are influenced by z3c.zalchemy (Juergen Kartnaller, Michael
Bernstein & others) and Alchemist/ore.alchemist (Kapil Thangavelu). Thanks to
Martin Aspeli for giving valuable feedback.

