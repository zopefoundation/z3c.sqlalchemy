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
from z3c.sqlalchemy.base import BaseWrapper, ZopeBaseWrapper

__all__ = ('createSQLAlchemyWrapper', 'registerSQLAlchemyWrapper', 'allRegisteredSQLAlchemyWrappers', 'getSQLAlchemyWrapper',
           'createSAWrapper', 'registerSAWrapper', 'allRegisteredSAWrappers', 'getSAWrapper', 'allSAWrapperNames')

registeredWrappers = {}

def createSAWrapper(dsn, model=None, forZope=False, name=None, transactional=True, **kw):
    """ Convenience method to generate a wrapper for a DSN and a model.
        This method hides all database related magic from the user. 

        'dsn' - something like 'postgres://user:password@host/dbname'

        'model' - None or  an instance of model.Model or a string representing
        a named utility implementing IModelProvider or a method/callable returning an
        instance of model.Model.

        'forZope' - set this to True in order to obtain a Zope-transaction-aware
        wrapper.

        'transactional' - True|False, only used for SQLAlchemyDA *don't change it*

        'name' can be set to register the wrapper automatically  in order
        to avoid a dedicated registerSAWrapper() call.
    """

    url = make_url(dsn)
    driver = url.drivername

    klass = forZope and ZopeBaseWrapper or BaseWrapper

    if driver == 'postgres':
        klass = forZope and ZopePostgresWrapper or PythonPostgresWrapper

    wrapper = klass(dsn, model, transactional, **kw)
    if name is not None:
        registerSAWrapper(wrapper, name)

    return wrapper

createSQLAlchemyWrapper = createSAWrapper


def registerSAWrapper(wrapper, name):
    """ deferred registration of the wrapper as named utility """

    if not registeredWrappers.has_key(name):
        registeredWrappers[name] = wrapper    

registerSQLAlchemyWrapper = registerSAWrapper

    
def _registerSAWrapper(wrapper, name):
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


def getSAWrapper(name):        
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
        _registerSAWrapper(wrapper, name)
        return wrapper

getSQLAlchemyWrapper = getSAWrapper


def allRegisteredSAWrappers():
    """ return a dict containing information for all
        registered wrappers.
    """

    for name, wrapper in getUtilitiesFor(ISQLAlchemyWrapper):
        yield {'name' : name,
               'dsn' : wrapper.dsn,
               'kw' : wrapper.kw,
              }

allRegisteredSQLAlchemyWrappers = allRegisteredSAWrappers


def allSAWrapperNames():
    """ return list of all registered wrapper names """
    names = registeredWrappers.keys()
    return sorted(names)


if __name__ == '__main__':
    print createSAWrapper('postgres://test:test@db.example.com/TestDB', forZope=True)
