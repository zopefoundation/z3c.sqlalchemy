##########################################################################
# z3c.sqlalchemy - A SQLAlchemy wrapper for Python/Zope
#
# (C) Zope Corporation and Contributor
# Written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
# and ZOPYX Ltd. & Co. KG, Tuebingen, Germany
##########################################################################

import threading

import sqlalchemy
from sqlalchemy.engine.url import make_url

from zope.interface import implements
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError

from z3c.sqlalchemy.interfaces import ISQLAlchemyWrapper, IModelProvider
from z3c.sqlalchemy.model import Model
from z3c.sqlalchemy.mapper import LazyMapperCollection

import transaction
from transaction.interfaces import IDataManager


class BaseWrapper(object):

    implements(ISQLAlchemyWrapper)

    def __init__(self, dsn, model=None, echo=False):
        """ 'dsn' - a RFC-1738-style connection string

            'model' - optional instance of model.Model

            'echo' - output generated SQL commands
        """

        self.dsn = dsn
        self.url = make_url(dsn)
        self.host = self.url.host
        self.port = self.url.port
        self.username = self.url.username
        self.password = self.url.password
        self.dbname = self.url.database 
        self.drivername = self.url.drivername
        self.echo = echo
        self._engine = self._createEngine()
        self._engine.echo = echo
        self._model = None

        if model:
            if isinstance(model, Model):
                self._model = model

            elif isinstance(model, basestring):
                try:
                    util = getUtility(IModelProvider, model)
                except ComponentLookupError:
                    raise ComponentLookupError("No named utility '%s' providing IModelProvider found" % model)


                self._model = util.getModel()

            else:
                raise ValueError("The 'model' parameter passed to constructor must either be "\
                                 "the name of a named utility implementing IModelProvider or "\
                                 "an instance of haufe.sqlalchemy.model.Model.")

        # mappers must be initialized at last since we need to acces
        # the 'model' from within the constructor of LazyMapperCollection
        self._mappers = LazyMapperCollection(self)

    @property
    def metadata(self):
        return sqlalchemy.BoundMetaData(self._engine)

    @property
    def session(self):
        return sqlalchemy.create_session(self._engine)

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
        return sqlalchemy.create_engine(self.dsn)


_cache = threading.local() # module-level cache 

class DataManager(object):
    """ Wraps session into transaction context of Zope """

    implements(IDataManager)

    def __init__(self, session):
        self.session = session
        self.transaction = session.create_transaction()

    def tpc_begin(self, trans):
        pass

    def abort(self):
        self.transaction.rollback()

    def commit(self, trans):
        self.session.flush()
        self.transaction.commit()

    def tpc_vote(self, trans):
        pass

    def tpc_finish(self, trans):
        pass

    def tpc_abort(self, trans):
        pass

    def sortKey(self):
        return str(id(self))


class ZopeBaseWrapper(BaseWrapper):
    """ A wrapper to be used from within Zope. It connects
        the session with the transaction management of Zope.
    """

    @property
    def session(self):

        if not hasattr(_cache, 'last_transaction'):
            _cache.last_transaction = None
            _cache.last_session = None

        # get current transaction
        txn = transaction.get()
        txn_str = str(txn)

        # return cached session if we are within the same transaction
        # and same thread
        if txn_str == _cache.last_transaction:
            return _cache.last_session

        # no cached session, let's create a new one
        session = sqlalchemy.create_session(self._engine)
                                          
        # register a DataManager with the current transaction
        DM = DataManager(session)  # no, 'DM' does not mean Dieter Maurer
        txn.join(DM)

        # update thread-local cache
        _cache.last_transaction = txn_str
        _cache.last_session = session

        # return the session
        return session 

