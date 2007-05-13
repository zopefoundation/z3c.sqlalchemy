# -*- coding: iso-8859-15 -*-

##########################################################################
# z3c.sqlalchemy - A SQLAlchemy wrapper for Python/Zope
#
# (C) Zope Corporation and Contributor
# Written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
# and ZOPYX Ltd. & Co. KG, Tuebingen, Germany
##########################################################################


"""
Tests, tests, tests.........
"""

import unittest
import sqlalchemy

from zope.interface.verify import verifyClass

from z3c.sqlalchemy.interfaces import ISQLAlchemyWrapper, IModel
from z3c.sqlalchemy.postgres import PythonPostgresWrapper,  ZopePostgresWrapper
from z3c.sqlalchemy.base import BaseWrapper
from z3c.sqlalchemy.mapper import MappedClassBase
from z3c.sqlalchemy import createSAWrapper, Model, registerSAWrapper, getSAWrapper


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
                    """                  lastname varchar(255)"""
                    """)""")

        try:
            cur.execute("""DROP TABLE skills""")
        except:
            pass
        cur.execute("""CREATE TABLE skills(id int4 primary key,"""
                    """                    user_id int4, """
                    """                    name varchar(255)"""
                    """)""")
        db.close()


    def testIFaceBaseWrapper (self):
        verifyClass(ISQLAlchemyWrapper , BaseWrapper)


    def testIFacePythonPostgres(self):
        verifyClass(ISQLAlchemyWrapper , PythonPostgresWrapper)


    def testIFaceZopePostgres(self):
        verifyClass(ISQLAlchemyWrapper , ZopePostgresWrapper)

    def testIModel(self):
        verifyClass(IModel, Model)


    def testSimplePopulation(self):
        db = createSAWrapper('sqlite:///test')
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

        class myUser(MappedClassBase): 
            pass

        M = Model()
        M.add('user', mapper_class=myUser)

        db = createSAWrapper('sqlite:///test', model=M)
        User = db.getMapper('user')
        self.assertEqual(User, myUser)


    def testCustomMapperClassWithWrongType(self):

        class myUser(object): 
            pass

        M = Model()
        self.assertRaises(TypeError, M.add, 'user', mapper_class=myUser)


    def testGetMappers(self):

        db = createSAWrapper('sqlite:///test')
        Users = db.getMapper('user')
        Skills = db.getMapper('skills')
        User, Skills = db.getMappers('user', 'skills')


    def testModelWeirdParameters(self):
        M = Model()
        self.assertRaises(ValueError, M.add, 'user', relations=('foo', 'bar'), autodetect_relations=True)

    def testModelWeirdRelationsParameters(self):
        M = Model()
        self.assertRaises(TypeError, M.add, 'user', relations=('foo'))

    def testModelNonExistingTables(self):
        M = Model()
        M.add('non_existing_table')
        db = createSAWrapper('sqlite:///test', model=M)
        try:
            foo = db.getMapper('non_existing_table')
        except sqlalchemy.exceptions.NoSuchTableError:
            pass


    def testWrapperRegistration(self):
        wrapper = createSAWrapper('sqlite:///test')
        registerSAWrapper(wrapper, 'test.wrapper1')
        wrapper2 = getSAWrapper('test.wrapper1')
        self.assertEqual(wrapper, wrapper2)

    
    def testWrapperRegistrationFailing(self):
        wrapper = createSAWrapper('sqlite:///test')
        registerSAWrapper(wrapper, 'test.wrapper2')
        self.assertRaises(ValueError, getSAWrapper, 'test.wrapperNonExistant')


    def testWrapperDirectRegistration(self):
        wrapper = createSAWrapper('sqlite:///test', name='test.wrapper3')
        wrapper2 = getSAWrapper('test.wrapper3')
        self.assertEqual(wrapper, wrapper2)

        
    def testMapperGetMapper(self):

        def getModel(md):

            model = Model()
            model.add('user', table=sqlalchemy.Table('user', md, autoload=True), relations=('skills',))
            model.add('skills', table=sqlalchemy.Table('skills', 
                                                       md, 
                                                       sqlalchemy.ForeignKeyConstraint(('user_id',), ('user.id',)),
                                                       autoload=True, 
                                                       ))
            return model

        db = createSAWrapper('sqlite:///test', model=getModel)
        User = db.getMapper('user')
        session = db.session
        session.save(User(id=1,firstname='foo', lastname='bar'))
        session.flush()
        user = session.query(User).select_by(firstname='foo')[0]
        Skill = user.getMapper('skills')
        user.skills.append(Skill(id=1, name='Zope'))
        session.flush()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(WrapperTests))
    return suite

