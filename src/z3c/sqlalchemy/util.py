##########################################################################
# z3c.sqlalchemy - A SQLAlchemy wrapper for Python/Zope
#
# (C) Zope Corporation and Contributor
# Written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
# and ZOPYX Ltd. & Co. KG, Tuebingen, Germany
##########################################################################


""" 
Some helper methods
"""


from sqlalchemy.engine.url import make_url

from zope.component import getService, getGlobalServices, getUtilitiesFor, provideUtility 
from zope.component.utility import GlobalUtilityService
from zope.component.interfaces import IUtilityService
from zope.component.servicenames import Utilities 

from z3c.sqlalchemy.interfaces import ISQLAlchemyWrapper
from z3c.sqlalchemy.postgres import ZopePostgresWrapper, PythonPostgresWrapper 
from z3c.sqlalchemy.base import BaseWrapper

__all__ = ('createSQLAlchemyWrapper', 'registerSQLAlchemyWrapper', 'allRegisteredSQLAlchemyWrappers')


def createSQLAlchemyWrapper(dsn, model=None, echo=False, forZope=False):
    """ Convenience method to generate a wrapper for a DSN and a model.
        This method hides all database related magic from the user. 
        Set 'forZope' to True for a Zope related wrapper.
    """

    url = make_url(dsn)
    driver = url.drivername

    klass = BaseWrapper

    if driver == 'postgres':
        klass = forZope and ZopePostgresWrapper or PythonPostgresWrapper

    return klass(dsn, echo=echo, model=model)


def registerSQLAlchemyWrapper(wrapper, name):
    """ register a SQLAlchemyWrapper as named utility """

    # Bootstrap utility service
    try:
        # Zope 2.8
        sm = getGlobalServices()
        sm.defineService(Utilities, IUtilityService)
        sm.provideService(Utilities, GlobalUtilityService())

        # register wrapper 
        utilityService = getService(Utilities)
        utilityService.provideUtility(ISQLAlchemyWrapper, wrapper, name)

    except NotImplementedError:
        # Zope 2.9+
        provideUtility(wrapper, name=name)

def allRegisteredSQLAlchemyWrappers():
    """ return a dict containing information for all
        registered wrappers.
    """

    for name, wrapper in getUtilitiesFor(ISQLAlchemyWrapper):
        yield {'name' : name,
               'dsn' : wrapper.dsn,
               'echo' : wrapper.echo,
              }


if __name__ == '__main__':
    print createWrapper('postgres://test:test@db.example.com/TestDB', None)
