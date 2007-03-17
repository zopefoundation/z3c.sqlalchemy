##########################################################################
# z3c.sqlalchemy - A SQLAlchemy wrapper for Python/Zope
#
# (C) Zope Corporation and Contributor
# Written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
# and ZOPYX Ltd. & Co. KG, Tuebingen, Germany
##########################################################################


import sys
import threading

import sqlalchemy

from zope.interface import implements

from z3c.sqlalchemy.interfaces import ISQLAlchemyWrapper
from z3c.sqlalchemy.base import BaseWrapper

import transaction
from transaction.interfaces import IDataManager

_cache = threading.local() # module-level cache 

marker = object


class DataManager(object):
    """ Wraps session into transaction context of Zope """

    implements(IDataManager)

    def __init__(self, session):
        self.session = session

    def abort(self, trans):
        pass

    def tpc_begin(self, trans):
        pass

    def commit(self, trans):
        self.session.flush()

    def tpc_vote(self, trans):
        pass

    def tpc_finish(self, trans):
        pass

    def tpc_abort(self, trans):
        pass

    def sortKey(self):
        return str(id(self))



class ZopeMixin:
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
        DM = DataManager(session)
        txn.join(DM)

        # update thread-local cache
        _cache.last_transaction = txn_str
        _cache.last_session = session

        # return the session
        return session 

class ZopeBaseWrapper(BaseWrapper, ZopeMixin):
    """ A generic wrapper for Zope """
