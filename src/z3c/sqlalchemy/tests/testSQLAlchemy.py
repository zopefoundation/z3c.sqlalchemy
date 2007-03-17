# -*- coding: iso-8859-15 -*-

##########################################################################
# z3c.sqlalchemy - A SQLAlchemy wrapper for Python/Zope
#
# (C) 2007, Haufe-Mediengruppe, Freiburg, Germany
# (C) 2007, ZOPYX Ltd. & Co. KG, Tuebingen, Germany
# 
# Published under the Zope Public License V 2.1 
##########################################################################


"""
Tests, tests, tests.........
"""


import os
import sys
import unittest

import sqlalchemy

from zope.interface.verify import verifyClass
from z3c.sqlalchemy.interfaces import ISQLAlchemyWrapper
from z3c.sqlalchemy.postgres import PythonPostgresWrapper,  ZopePostgresWrapper
from z3c.sqlalchemy.base import BaseWrapper
from z3c.sqlalchemy import createSQLAlchemyWrapper, Model

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


class WrapperTests(unittest.TestCase):


    def setUp(self):
        from pysqlite2 import dbapi2 as sqlite

        db = sqlite.connect('test')
        cur = db.cursor()
        try:
            cur.execute("""DROP TABLE user""")
        except:
            pass

        cur.execute("""CREATE TABLE user(id int4 primary key,"""
                    """                  firstname varchar(255),"""
                    """                  lasttname varchar(255)"""
                    """)""")

        try:
            cur.execute("""DROP TABLE skills""")
        except:
            pass
        cur.execute("""CREATE TABLE skills(id int4 primary key,"""
                    """                    user_id int4, """
                    """                    name varchar(255),"""
                    """                    FOREIGN KEY (user_id) REFERENCES xxxx"""
                    """)""")
        db.close()

    def testIFaceBaseWrapper (self):
        verifyClass(ISQLAlchemyWrapper , BaseWrapper)

    def testIFacePythonPostgres(self):
        verifyClass(ISQLAlchemyWrapper , PythonPostgresWrapper)

    def testIFaceZopePostgres(self):
        verifyClass(ISQLAlchemyWrapper , ZopePostgresWrapper)

    def testSimplePopulation(self):
        db = createSQLAlchemyWrapper('sqlite:///test')
        # obtain mapper for table 'user'

        User = db.getMapper('user')
        session = db.session

        rows = session.query(User).select()
        self.assertEqual(len(rows), 0)

        session.save(User(id=1, firstname='udo', lastname='juergens'))
        session.save(User(id=2, firstname='heino', lastname='n/a'))
        session.flush()
        
        rows = session.query(User).select()
        self.assertEqual(len(rows), 2)

    def testMapperWithCustomModel(self):

        class myUser(object): 
            pass

        M = Model()
        M.add('user', mapper_class=myUser)

        db = createSQLAlchemyWrapper('sqlite:///test', model=M)
        User = db.getMapper('user')
        self.assertEqual(User, myUser)


    def testModelWeirdParameters(self):
        M = Model()
        self.assertRaises(ValueError, M.add, 'user', relations=('foo', 'bar'), autodetect_relations=True)

    def testModelNonExistingTables(self):
        M = Model()
        M.add('non_existing_table')
        db = createSQLAlchemyWrapper('sqlite:///test', model=M)
        try:
            foo = db.getMapper('nonn_existing_table')
        except sqlalchemy.exceptions.NoSuchTableError:
            pass


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(WrapperTests))
    return suite

if __name__ == '__main__':
    framework()
