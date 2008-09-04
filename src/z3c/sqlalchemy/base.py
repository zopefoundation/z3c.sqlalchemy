##########################################################################
# z3c.sqlalchemy - A SQLAlchemy wrapper for Python/Zope
#
# (C) Zope Corporation and Contributor
# Written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
# and ZOPYX Ltd. & Co. KG, Tuebingen, Germany
##########################################################################

from zope.interface import implements
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError

from z3c.sqlalchemy.model import Model
from z3c.sqlalchemy.mapper import LazyMapperCollection
from z3c.sqlalchemy.interfaces import ISQLAlchemyWrapper, IModelProvider


from sqlalchemy import create_engine, MetaData
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import scoped_session, sessionmaker, relation
from zope.sqlalchemy import ZopeTransactionExtension


class ZopeWrapper(object):

    implements(ISQLAlchemyWrapper)

    def __init__(self, dsn, model=None, transactional=True, 
                 engine_options={}, session_options={}, 
                 extension_options={}, **kw):
        """ 'dsn' - a RFC-1738-style connection string

            'model' - optional instance of model.Model

            'engine_options' - optional keyword arguments passed to
            create_engine()

            'session_options' - optional keyword arguments passed to
            create_session() or sessionmaker()

            'extension_options' - optional keyword argument passed to 
            ZopeTransactionExtension()

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
        self.extension_options = extension_options
        self._model = None
        self._createEngine()

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
            self._v_metadata = MetaData(self._engine)
        return self._v_metadata

    @property
    def session(self):
        """ Return thread-local session """
        return self._sessionmaker()

    @property
    def connection(self):
        """ Return underlying connection """
        session = self.session
        # Return the ConnectionFairy
        return session.connection().connection
        # instead of the raw connection
        #return session.connection().connection.connection

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
        self._engine = create_engine(self.dsn, **self.engine_options)
        self._sessionmaker = scoped_session(sessionmaker(bind=self._engine, 
                                            autocommit=False, 
                                            autoflush=True, 
                                            extension=ZopeTransactionExtension(self.extension_options),
                                            **self.session_options
                                            ))
