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

import os
import unittest
import sqlalchemy

from sqlalchemy import MetaData, Integer, String, Column, Table

from zope.interface.verify import verifyClass

from z3c.sqlalchemy.interfaces import ISQLAlchemyWrapper, IModel
from z3c.sqlalchemy.postgres import PythonPostgresWrapper,  ZopePostgresWrapper
from z3c.sqlalchemy.base import BaseWrapper
from z3c.sqlalchemy.mapper import MappedClassBase
from z3c.sqlalchemy import createSAWrapper, Model, registerSAWrapper, getSAWrapper


class WrapperTests(unittest.TestCase):

    def setUp(self):

        self.dsn = os.environ.get('TEST_DSN', 'sqlite:///test')
        wrapper = createSAWrapper(self.dsn)
        metadata = MetaData(bind=wrapper.engine)

        users = Table('users', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('firstname', String),
                      Column('lastname', String))

        skill = Table('skills', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('user_id', Integer),
                      Column('name', String))

        metadata.create_all()


    def testIFaceBaseWrapper (self):
        verifyClass(ISQLAlchemyWrapper , BaseWrapper)


    def testIFacePythonPostgres(self):
        verifyClass(ISQLAlchemyWrapper , PythonPostgresWrapper)


    def testIFaceZopePostgres(self):
        verifyClass(ISQLAlchemyWrapper , ZopePostgresWrapper)

    def testIModel(self):
        verifyClass(IModel, Model)


    def testSimplePopulation(self):
        db = createSAWrapper(self.dsn)
        # obtain mapper for table 'users'

        User = db.getMapper('users')
        session = db.session

        rows = session.query(User).all()
        self.assertEqual(len(rows), 0)

        session.save(User(id=1, firstname='udo', lastname='juergens'))
        session.save(User(id=2, firstname='heino', lastname='n/a'))
        session.flush()
        
        rows = session.query(User).order_by(User.c.id).all()
        self.assertEqual(len(rows), 2)
        row1 = rows[0]
        d = row1.asDict()
        self.assertEqual(d, {'firstname' : 'udo', 'lastname' : 'juergens', 'id' : 1})


    def testMapperWithCustomModel(self):

        class myUser(MappedClassBase): 
            pass

        M = Model()
        M.add('users', mapper_class=myUser)

        db = createSAWrapper(self.dsn, model=M)
        User = db.getMapper('users')
        self.assertEqual(User, myUser)


    def testCustomMapperClassWithWrongType(self):

        class myUser(object): 
            pass

        M = Model()
        self.assertRaises(TypeError, M.add, 'users', mapper_class=myUser)


    def testGetMappers(self):

        db = createSAWrapper(self.dsn)
        Users = db.getMapper('users')
        Skills = db.getMapper('skills')
        User, Skills = db.getMappers('users', 'skills')


    def testModelWeirdParameters(self):
        M = Model()
        self.assertRaises(ValueError, M.add, 'users', relations=('foo', 'bar'), autodetect_relations=True)

    def testModelWeirdRelationsParameters(self):
        M = Model()
        self.assertRaises(TypeError, M.add, 'users', relations=('foo'))

    def testModelNonExistingTables(self):
        M = Model()
        M.add('non_existing_table')
        db = createSAWrapper(self.dsn, model=M)
        try:
            foo = db.getMapper('non_existing_table')
        except sqlalchemy.exceptions.NoSuchTableError:
            pass


    def testWrapperRegistration(self):
        wrapper = createSAWrapper(self.dsn)
        registerSAWrapper(wrapper, 'test.wrapper1')
        wrapper2 = getSAWrapper('test.wrapper1')
        self.assertEqual(wrapper, wrapper2)

    
    def testWrapperRegistrationFailing(self):
        wrapper = createSAWrapper(self.dsn)
        self.assertRaises(ValueError, getSAWrapper, 'test.wrapperNonExistant')


    def testWrapperDoubleRegistrationFailing(self):
        wrapper = createSAWrapper(self.dsn)
        registerSAWrapper(wrapper, 'test.wrapper2')
        self.assertRaises(ValueError, registerSAWrapper, wrapper, 'test.wrapper2')


    def testWrapperDirectRegistration(self):
        wrapper = createSAWrapper(self.dsn, name='test.wrapper3')
        wrapper2 = getSAWrapper('test.wrapper3')
        self.assertEqual(wrapper, wrapper2)

        
    def testXXMapperGetMapper(self):
        def getModel(md):

            model = Model()
            model.add('users', table=sqlalchemy.Table('users', md, autoload=True), relations=('skills',))
            model.add('skills', table=sqlalchemy.Table('skills', 
                                                       md, 
                                                       sqlalchemy.ForeignKeyConstraint(('user_id',), ('users.id',)),
                                                       autoload=True, 
                                                       ))
            return model

        db = createSAWrapper(self.dsn, model=getModel)
        User = db.getMapper('users')
        session = db.session
        session.save(User(id=1,firstname='foo', lastname='bar'))

        user = session.query(User).filter_by(firstname='foo')[0]
        Skill = user.getMapper('skills')
        user.skills.append(Skill(id=1, name='Zope'))
        session.flush()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(WrapperTests))
    return suite

