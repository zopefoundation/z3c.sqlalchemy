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
from zope import interface
from zope import schema
from zope.app.container.interfaces import IContainerNamesContainer
from zope.app.container.constraints import contains, containers


class ISQLAlchemyObject(interface.Interface):
    """Marker interface for mapped sqlalchemy objects.
    """


class ISQLAlchemyContainer(IContainerNamesContainer):
    """A zope container containing sqlalchemy objects.
    """
    className = schema.TextLine(
            title = u'Class',
            required = True,
            )
    contains(ISQLAlchemyObject)


class ISQLAlchemyObjectContained(interface.Interface):
    """Limit containment to SQLAlchemy containers
    """
    containers(ISQLAlchemyContainer)


class IAlchemyEngineUtility(interface.Interface):
    dsn = schema.URI(
            title=u'DSN',
            required=True,
            default='sqlite://',
            )
    encoding = schema.BytesLine(
            title=u'Encoding',
            required=True,
            default='utf-8',
            )
    convert_unicode = schema.Bool(
            title=u'Convert Unicode',
            required=False,
            default=False
            )
    echo = schema.Bool(
            title=u'Echo SQL',
            required=False,
            default=False
            )

class IAlchemy(interface.Interface):
    
    def getSession(createTransaction=False):
        """Get a new session for the current thread.

        createTransaction :
            Create a zope transaction if none exists for the current thread.
        """

    def inSession():
        """Return True if the thread is in a transaction.
        """

    def assignTable(table, engine):
        """Assign a table to an engine.
        The table is immediately assigned to the engine if a session is active
        for the thread. If no session is active the table is assigned when the
        next session starts.

        table :
            Name of the table.
        engine :
            Name of the engine utility.
        """

    def assignClass(class_, engine):
        """Assign a class to an engine.
        The class is immediately assigned to the engine if a session is active
        for the thread. If no session is active the class is assigned when the
        next session starts.

        class_ :
            The class to assign to an engine.
            The class must have a primary mapper assigned.
        engine :
            Name of the engine utility.
        """

    def createTable(table, engine=''):
        """Automatically create a table in the database.
        The table is immediately created if a session is active for the thread.
        If no session is active the table is created when the next session
        starts.

        table :
            Name of the table.
        engine :
            Name of the engine utility.
        """

    def dropTable(table, engine=''):
        """Drop a table.

        Drops the table immediately without the need of a session.

        table :
            Name of the table.
        engine :
            Name of the engine utility.
        """

    def getEngineForTable(t):
        """returns an sqlalchemy engine for the given table name, this is
           usefull for using the engine to execute literal sql statements
        """


class IConflictError(interface.Interface):
    """Two transactions tried to modify the same object at once.

    Exceptions occuring on commit/flush will be adapted to this interface.
    Registered adapters must either return an ZODB.POSException.ConflictError
    or None. A ConflictError will tell the publisher to retry the transaction.

    """
