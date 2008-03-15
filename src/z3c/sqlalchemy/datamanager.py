##############################################################################
#
# Copyright (c) 2006 ROBOTECH Logistiksysteme GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import persistent
import transaction
from zope.interface import implements
from zope.component import queryUtility, getUtility, getUtilitiesFor
from zope.schema.fieldproperty import FieldProperty

from transaction.interfaces import IDataManager, ISynchronizer
from transaction.interfaces import IDataManagerSavepoint

import z3c.zalchemy.interfaces

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.orm.mapper import global_extensions

from sqlalchemy.orm import scoped_session, sessionmaker


class AlchemyEngineUtility(persistent.Persistent):
    """A utility providing a database engine.
    """

    implements(z3c.zalchemy.interfaces.IAlchemyEngineUtility)

    def __init__(self, name, dsn, echo=False, encoding='utf-8',
                 convert_unicode=False, **kwargs):
        self.name = name
        self.dsn = dsn
        self.encoding = encoding
        self.convert_unicode = convert_unicode
        self.echo = echo
        self.kw={}
        self.kw.update(kwargs)

    def getEngine(self):
        engine = getattr(self, '_v_engine', None)
        if engine:
            return engine
        # create_engine consumes the keywords, so better to make a copy first
        kw = {}
        kw.update(self.kw)
        # create a new engine and configure it thread-local
        self._v_engine = sqlalchemy.create_engine(
            self.dsn, echo=self.echo, encoding=self.encoding,
            convert_unicode=self.convert_unicode,
            strategy='threadlocal', **kw)
        return self._v_engine

    def _resetEngine(self):
        engine = getattr(self, '_v_engine', None)
        if engine is not None:
            engine.dispose()
            self._v_engine = None


for name in z3c.zalchemy.interfaces.IAlchemyEngineUtility:
    setattr(AlchemyEngineUtility, name, FieldProperty(
        z3c.zalchemy.interfaces.IAlchemyEngineUtility[name]))


_tableToEngine = {}
_classToEngine = {}
_tablesToCreate = []

# SQLAlchemy session management through thread-locals and our own data
# manager.

def createSession():
    """Creates a new session that is bound to the default engine utility and
    hooked up with the Zope transaction machinery.

    """
    util = queryUtility(z3c.zalchemy.interfaces.IAlchemyEngineUtility)
    if util is None:
        raise ValueError("No engine utility registered")
    engine = util.getEngine()
    session = SessionFactory(bind=engine)

    # This session is now only bound to the default engine. We need to bind
    # the other explicitly bound tables and classes as well.
    bind_session(session)

    transaction.get().join(AlchemyDataManager(session))
    return session

SessionFactory = sessionmaker(autoflush=True, transactional=True)
Session = scoped_session(createSession)


def bind_session(session):
    """Applies all table and class bindings to the given session."""
    for table, engine in _tableToEngine.items():
        _assignTable(table, engine, session)
    for class_, engine in _classToEngine.items():
        _assignClass(class_, engine, session)


def getSession():
    return Session()


def getEngineForTable(t):
    name = _tableToEngine[t]
    util = getUtility(z3c.zalchemy.interfaces.IAlchemyEngineUtility,
                      name=name)
    return util.getEngine()


def inSession():
    return True


def assignTable(table, engine, immediate=True):
    """Assign a table to an engine and propagate the binding to the current
    session.

    The binding is not applied to the current session if `immediate` is False.

    """
    _tableToEngine[table]=engine
    if immediate:
        _assignTable(table, engine)


def assignClass(class_, engine, immediate=True):
    """Assign a class to an engine and propagate the binding to the current
    session.

    The binding is not applied to the current session if `immediate` is False.

    """
    _classToEngine[class_]=engine
    if immediate:
        _assignClass(class_, engine)


def createTable(table, engine):
    _tablesToCreate.append((table, engine))
    _createTables()


def _assignTable(table, engine, session=None):
    t = metadata.getTable(engine, table, True)
    util = getUtility(z3c.zalchemy.interfaces.IAlchemyEngineUtility,
                      name=engine)
    if session is None:
            session = Session()
    session.bind_table(t, util.getEngine())


def _assignClass(class_, engine, session=None):
    m = sqlalchemy.orm.class_mapper(class_)
    util = getUtility(z3c.zalchemy.interfaces.IAlchemyEngineUtility,
                      name=engine)
    if session is None:
        session = Session()
    session.bind_mapper(m,util.getEngine())


def _createTables():
    tables = _tablesToCreate[:]
    del _tablesToCreate[:]
    for table, engine in tables:
        _doCreateTable(table, engine)


def _doCreateTable(table, engine):
    util = getUtility(z3c.zalchemy.interfaces.IAlchemyEngineUtility,
                      name=engine)
    t = metadata.getTable(engine, table, True)
    try:
        util.getEngine().create(t)
    except:
        pass


def dropTable(table, engine=''):
    util = getUtility(z3c.zalchemy.interfaces.IAlchemyEngineUtility,
                      name=engine)
    t = metadata.getTable(engine, table, True)
    try:
        util.getEngine().drop(t)
    except:
        pass


class AlchemyDataManager(object):
    """Takes care of the transaction process in Zope. """

    implements(IDataManager)

    def __init__(self, session):
        self.session = session

    def abort(self, trans):
        self._abort()

    def commit(self, trans):
        # Flush instructions to the database (because of conflict integration)
        self._flush_session()
        # Commit any nested transactions (savepoints)
        while self.session.transaction.nested:
            self.session.commit()

    def tpc_begin(self, trans):
        pass

    def tpc_vote(self, trans):
        pass

    def tpc_finish(self, trans):
        self.session.commit()
        self._cleanup()

    def tpc_abort(self, trans):
        self._abort()

    def sortKey(self):
        return str(id(self))

    def savepoint(self):
        self._flush_session()
        transaction = self.session.begin_nested()
        self._flush_session()
        return AlchemySavepoint(transaction, self.session)

    def _cleanup(self):
        Session.remove()

    def _abort(self):
        while self.session.transaction.nested:
            self.session.transaction.close()
        self.session.rollback()
        self._cleanup()

    def _flush_session(self):
        try:
            self.session.flush()
        except Exception, e:
            conflict = z3c.zalchemy.interfaces.IConflictError(e, None)
            if conflict is None:
                raise
            raise conflict


class AlchemySavepoint(object):
    """A savepoint for the AlchemyDataManager that only supports optimistic
    savepoints.

    """

    implements(IDataManagerSavepoint)

    def __init__(self, transaction, session):
        self.transaction = transaction
        self.session = session

    def rollback(self):
        # Savepoints expire the objects so they get reloaded with the old
        # state
        self.transaction.rollback()
        for obj in self.session:
            self.session.expire(obj)


class MetaManager(object):
    """A manager for metadata to be able to use the same table name in
    different databases.
    """

    def __init__(self):
        self.metadata = {}

    def getTable(self, engine, table, fallback):
        md = self.metadata.get(engine)
        if md and table in md.tables:
            return md.tables[table]
        if fallback and engine:
            md = self.metadata.get('')
        if md and table in md.tables:
            return md.tables[table]
        return None

    def __call__(self, engine=''):
        md = self.metadata.get(engine)
        if md is None:
            md = self.metadata[engine] = sqlalchemy.MetaData()
        return md


metadata = MetaManager()

