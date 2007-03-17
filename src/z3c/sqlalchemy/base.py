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
from z3c.sqlalchemy.odict import OrderedDict
from z3c.sqlalchemy.mapper import MapperFactory, LazyMapperCollection

import transaction


_cache = threading.local() # module-level cache 

marker = object


class BaseWrapper(object):

    implements(ISQLAlchemyWrapper)

    def __init__(self, dsn, model=None, echo=False):
        """ 'dsn' - an RFC-1738-style connection string

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
                    raise ComponentLookupError("No named utility '%s' implementing IModelProvider found" % model)


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

