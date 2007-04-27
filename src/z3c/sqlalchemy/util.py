##########################################################################
# z3c.sqlalchemy - A SQLAlchemy wrapper for Python/Zope
#
# (C) Zope Corporation and Contributors
# Written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
# and ZOPYX Ltd. & Co. KG, Tuebingen, Germany
##########################################################################


""" 
Some helper methods
"""


from sqlalchemy.engine.url import make_url

from zope.component import getService, getGlobalServices, getUtilitiesFor, getUtility
from zope.component.utility import GlobalUtilityService
from zope.component.interfaces import IUtilityService, ComponentLookupError
from zope.component.servicenames import Utilities 

from z3c.sqlalchemy.interfaces import ISQLAlchemyWrapper
from z3c.sqlalchemy.postgres import ZopePostgresWrapper, PythonPostgresWrapper 
from z3c.sqlalchemy.base import BaseWrapper

__all__ = ('createSQLAlchemyWrapper', 'registerSQLAlchemyWrapper', 'allRegisteredSQLAlchemyWrappers', 'getSQLAlchemyWrapper',
           'createSAWrapper', 'registerSAWrapper', 'allRegisteredSAWrappers', 'getSAWrapper')

registeredWrappers = {}

def createSQLAlchemyWrapper(dsn, model=None, forZope=False, **kw):
    """ Convenience method to generate a wrapper for a DSN and a model.
        This method hides all database related magic from the user. 
        Set 'forZope' to True to obtain a Zope-aware wrapper.
    """

    url = make_url(dsn)
    driver = url.drivername

    klass = forZope and ZopeBaseWrapper or BaseWrapper

    if driver == 'postgres':
        klass = forZope and ZopePostgresWrapper or PythonPostgresWrapper

    return klass(dsn, model, **kw)

createSAWrapper = createSQLAlchemyWrapper 


def registerSQLAlchemyWrapper(wrapper, name):
    """ deferred registration of the wrapper as named utility """

    if not registeredWrappers.has_key(name):
        registeredWrappers[name] = wrapper    

registerSAWrapper = registerSQLAlchemyWrapper
    
def _registerSQLAlchemyWrapper(wrapper, name):
    """ register a SQLAlchemyWrapper as named utility.
        (never call this method directly)
    """

    try:
        # Zope 2.9
        from zope.component import provideUtility
        provideUtility(wrapper, name=name)           
    except ImportError:
        # Zope 2.8
        from zope.component import getService, getGlobalServices, getUtilitiesFor
        from zope.component.utility import GlobalUtilityService
        from zope.component.interfaces import IUtilityService
        from zope.component.servicenames import Utilities
        sm = getGlobalServices()
        try:
            utilityService = getService(Utilities)
        except ComponentLookupError:
            sm.defineService(Utilities, IUtilityService)
            sm.provideService(Utilities, GlobalUtilityService())
            utilityService = getService(Utilities)

        utilityService.provideUtility(ISQLAlchemyWrapper, wrapper, name)


def getSQLAlchemyWrapper(name):        
    """ return a SQLAlchemyWrapper instance by name """

    if not registeredWrappers.has_key(name):    
        raise ValueError('No registered SQLAlchemyWrapper with name %s found' % name)

    # Perform a late and lazy registration of the wrapper as
    # named utility. Late initialization is necessary for Zope 2
    # application if you want to register wrapper instances during
    # the product initialization phase of Zope when the Z3 registries
    # are not yet initializied.

    try: 
        return getUtility(ISQLAlchemyWrapper, name)
    except ComponentLookupError:
        wrapper =  registeredWrappers[name]
        _registerSQLAlchemyWrapper(wrapper, name)
        return wrapper

getSAWrapper = getSQLAlchemyWrapper

def allRegisteredSQLAlchemyWrappers():
    """ return a dict containing information for all
        registered wrappers.
    """

    for name, wrapper in getUtilitiesFor(ISQLAlchemyWrapper):
        yield {'name' : name,
               'dsn' : wrapper.dsn,
               'kw' : wrapper.kw,
              }

allRegisteredSAWrappers = allRegisteredSQLAlchemyWrappers


if __name__ == '__main__':
    print createWrapper('postgres://test:test@db.example.com/TestDB', None)
