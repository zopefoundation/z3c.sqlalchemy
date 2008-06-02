##########################################################################
# z3c.sqlalchemy - A SQLAlchemy wrapper for Python/Zope
#
# (C) Zope Corporation and Contributor
# Written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
# and ZOPYX Ltd. & Co. KG, Tuebingen, Germany
##########################################################################


"""
Optional Model support 
"""

import sqlalchemy
from zope.interface import implements

from mapper import MappedClassBase
from interfaces import IModel

__all__ = ('Model',)


class Model(dict):
    """ The Model is an optional helper class that can be passed to the
        constructor of a SQLAlchemy wrapper in order to provide hints for the mapper
        generation.
    """        

    implements(IModel)

    def __init__(self, *args):
        """ The constructor can be called with a series of dict. Each dict
            represents a single table and its data (see add() method).
        """

        super(Model, self).__init__()
        self.names = []

        for d in args:
            self.add(**d)


    def add(self, name, table=None, mapper_class=None, relations=None, autodetect_relations=False, table_name=None, cascade=None):
        """ 'name'  -- name of table (no schema support so far!)

            'table' -- a sqlalchemy.Table instance (None, for autoloading)

            'mapper_class' -- an optional class to be used as mapper class for 'table'

            'relations' -- an optional list of table names referencing 'table'. This is used 
            for auto-constructing the relation properties of the mapper class.

            'autodetect_relations' -- try to autodetect the relationships between tables
            and auto-construct the relation properties of the mapper if
            'relations' is omitted (set to None)

            'table_name' -- optional full name of a table (e.g. 'someschema.sometable') if
            you want to use 'name' as alias for the table.

            'cascade' -- optional cascade parameter directly passed to the relation() call
        """

        if table is not None and not isinstance(table, sqlalchemy.Table):
            raise TypeError("'table' must be an instance or sqlalchemy.Table or None")

        # sqlalchemy.ext.declarative can be used on _any_ base class
#        if mapper_class is not None and not issubclass(mapper_class, MappedClassBase):
#            raise TypeError("'mapper_class' must be a subclass of MappedClassBase")

        if relations is not None:

            if not isinstance(relations, (tuple, list)):
                    raise TypeError('relations must be specified a sequence of strings')    

            for r in relations:
                if not isinstance(r, str):
                    raise TypeError('relations must be specified a sequence of strings')    

        if relations is not None and autodetect_relations == True:
            raise ValueError("'relations' and 'autodetect_relations' can't be specified at the same time")

        self.names.append(name)

        self[name] = {'name' : name,
                      'table' : table,
                      'relations' : relations,
                      'mapper_class' : mapper_class,
                      'autodetect_relations' : autodetect_relations,
                      'cascade' : cascade,
                      'table_name' : table_name,
                     }


    def items(self):
        """ return items in insertion order """

        for name in self.names:
            yield name, self[name]
                        

if __name__ == '__main__':

    m = Model()
    md = sqlalchemy.MetaData()
    m.add('users')
    m.add('groups', sqlalchemy.Table('groups', md,
                                     sqlalchemy.Column('id', sqlalchemy.Integer),
                                    ))
    m = Model()
    md = sqlalchemy.MetaData()
    m = Model({'name' : 'users'},
              {'name' : 'groups',
               'table' : sqlalchemy.Table('groups', md,
                                           sqlalchemy.Column('id', sqlalchemy.Integer),
                                         ),
              },
             )
    
