##########################################################################
# z3c.sqlalchemy - A SQLAlchemy wrapper for Python/Zope
#
# (C) Zope Corporation and Contributor
# Written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
# and ZOPYX Ltd. & Co. KG, Tuebingen, Germany
##########################################################################

import random
import threading

import sqlalchemy
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker

from zope.interface import implements
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError

from z3c.sqlalchemy.interfaces import ISQLAlchemyWrapper, IModelProvider
from z3c.sqlalchemy.model import Model
from z3c.sqlalchemy.mapper import LazyMapperCollection

import transaction
from transaction.interfaces import ISavepointDataManager, IDataManagerSavepoint


class SynchronizedThreadCache(object):

    def __init__(self):
        self.lock = threading.Lock()
        self.cache = threading.local()

    def set(self, id, d):
        self.lock.acquire()
        setattr(self.cache, id, d)
        self.lock.release()

    def get(self, id):
        self.lock.acquire()
        result = getattr(self.cache, id, None)
        self.lock.release()
        return result

    def remove(self, id):
        self.lock.acquire()
        if hasattr(self.cache, id):
            delattr(self.cache, id)           
        self.lock.release()



class BaseWrapper(object):

    implements(ISQLAlchemyWrapper)

    def __init__(self, dsn, model=None, transactional=True, engine_options={}, session_options={}, **kw):
        """ 'dsn' - a RFC-1738-style connection string

            'model' - optional instance of model.Model

            'engine_options' - optional keyword arguments passed to create_engine()

            'session_options' - optional keyword arguments passed to create_session() or sessionmaker()

            'transactional' - True|False, only used by SQLAlchemyDA, 
                              *don't touch it*
        """

        self.dsn = dsn
        self.url = make_url(dsn)
        self.host = self.url.host
        self.port = self.url.port
        self.username = self.url.username
        self.password = self.url.password
        self.dbname = self.url.database 
        self.drivername = self.url.drivername
        self.transactional = transactional
        self.engine_options = engine_options
        if 'echo' in kw:
            self.engine_options.update(echo=kw['echo'])
        self.session_options = session_options
        self._model = None
        self._createEngine()
        self._id = str(random.random()) # used as unique key for session/connection cache

        if model:

            if isinstance(model, Model):
                self._model = model

            elif isinstance(model, basestring):

                try:
                    util = getUtility(IModelProvider, model)
                except ComponentLookupError:
                    raise ComponentLookupError("No named utility '%s' providing IModelProvider found" % model)

                self._model = util.getModel(self.metadata)

            elif callable(model):                        
                self._model = model(self.metadata)

            else:
                raise ValueError("The 'model' parameter passed to constructor must either be "\
                                 "the name of a named utility implementing IModelProvider or "\
                                 "an instance of z3c.sqlalchemy.model.Model.")

            if not isinstance(self._model, Model):
                raise TypeError('_model is not an instance of model.Model')


        # mappers must be initialized at last since we need to acces
        # the 'model' from within the constructor of LazyMapperCollection
        self._mappers = LazyMapperCollection(self)

    @property
    def metadata(self):
        if not hasattr(self, '_v_metadata'):
            self._v_metadata = sqlalchemy.MetaData(self._engine)
        return self._v_metadata

    @property
    def session(self):
        return self._sessionmaker()

    def registerMapper(self, mapper, name):
        self._mappers.registerMapper(mapper, name)

    def getMapper(self, tablename, schema='public'):
        return self._mappers.getMapper(tablename, schema)

    def getMappers(self, *names):
        return tuple([self.getMapper(name) for name in names])

    @property
    def engine(self):
        """ only for private purposes! """
        return self._engine

    @property
    def model(self):
        """ only for private purposes! """
        return self._model

    def _createEngine(self):
        self._engine = sqlalchemy.create_engine(self.dsn, **self.engine_options)
        self._sessionmaker = sqlalchemy.orm.sessionmaker(bind=self._engine, 
                                                         autoflush=True,
                                                         transactional=True,
                                                         **self.session_options)


connection_cache = SynchronizedThreadCache()


class SessionDataManager(object):
    """ Wraps session into transaction context of Zope """

    implements(ISavepointDataManager)

    def __init__(self, connection, session, id, transactional=True):

        self.connection = connection
        self.session = session
        self.transactional = True
        self._id = id
        self.transaction = None
        if self.transactional:
            self.transaction = connection.begin()

    def abort(self, trans):

        try:
            if self.transaction is not None:
                self.transaction.rollback()
        # DM: done in "_cleanup" (similar untidy code at other places as well)
##        self.session.clear()
##        connection_cache.remove(self._id)
        finally:
            # ensure '_cleanup' is called even when 'rollback' causes an exception
            self._cleanup()

    def _flush(self):

        # check if the session contains something flushable
        if self.session.new or self.session.deleted or self.session.dirty:

            # Check if a session-bound transaction has been created so far.
            # If not, create a new transaction
#            if self.transaction is None:
#                self.transaction = connection.begin()

            # Flush
            self.session.flush()

    def commit(self, trans):
        self._flush()

    def tpc_begin(self, trans):
        pass

    def tpc_vote(self, trans):
        self._flush()

    def tpc_finish(self, trans):

        if self.transaction is not None:
            self.transaction.commit()

        self.session.clear()
        self._cleanup()
        

    # DM: no need to duplicate this code (identical to "abort")
##    def tpc_abort(self, trans):
##        if self.transaction is not None:
##            self.transaction.rollback()
##        self._cleanup()
    tpc_abort = abort

    def sortKey(self):
        return 'z3c.sqlalchemy_' + str(id(self))

    def _cleanup(self):
        self.session.clear()
        if self.connection:
            self.connection.close()
            self.connection = None
        connection_cache.remove(self._id)
        # DM: maybe, we should set "transaction" to "None"?

    def savepoint(self):
        """ return a dummy savepoint """
        return AlchemySavepoint()



# taken from z3c.zalchemy

class AlchemySavepoint(object):
    """A dummy saveoint """

    implements(IDataManagerSavepoint)

    def __init__(self):
        pass

    def rollback(self):
        pass



class ZopeBaseWrapper(BaseWrapper):
    """ A wrapper to be used from within Zope. It connects
        the session with the transaction management of Zope.
    """


    def __getOrCreateConnectionCacheItem(self, cache_id):

        cache_item = connection_cache.get(cache_id)

        # return cached session if we are within the same transaction
        # and same thread
        if cache_item is not None:
            return cache_item

        # no cached session, let's create a new one
        connection = self.engine.connect()
        session = sessionmaker(connection)()
                                          
        # register a DataManager with the current transaction
        transaction.get().join(SessionDataManager(connection, session, self._id))

        # update thread-local cache
        cache_item = dict(connection=connection, session=session)
        connection_cache.set(self._id, cache_item)
        return cache_item


    @property
    def session(self):
        """ Return a (cached) session object for the current transaction """
        return self.__getOrCreateConnectionCacheItem(self._id)['session']


    @property
    def connection(self):
        """ This property is _private_ and only intented to be used
            by SQLAlchemyDA and therefore it is not part of the 
            public API. 
        """
    
        return self.__getOrCreateConnectionCacheItem(self._id)['connection']
