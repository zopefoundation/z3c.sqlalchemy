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
import tempfile
import unittest

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import exc
from sqlalchemy.orm import declarative_base
from zope.interface.verify import verifyClass

from z3c.sqlalchemy import Model
from z3c.sqlalchemy import createSAWrapper
from z3c.sqlalchemy import getSAWrapper
from z3c.sqlalchemy import registerSAWrapper
from z3c.sqlalchemy.interfaces import IModel
from z3c.sqlalchemy.interfaces import ISQLAlchemyWrapper
from z3c.sqlalchemy.mapper import MappedClassBase
from z3c.sqlalchemy.postgres import ZopePostgresWrapper


class WrapperTests(unittest.TestCase):

    def setUp(self):

        self.dsn = os.environ.get('TEST_DSN')
        self.tempfile = None
        if not self.dsn:
            self.tempfile = tempfile.mktemp()
            self.dsn = 'sqlite:///%s' % self.tempfile
        self.db = wrapper = createSAWrapper(self.dsn)
        metadata = MetaData()

        Table('users', metadata,
              Column('id', Integer, primary_key=True),
              Column('firstname', String(255)),
              Column('lastname', String(255)))

        Table('skills', metadata,
              Column('user_id', Integer, primary_key=True),
              Column('name', String(255)))

        metadata.create_all(bind=wrapper.engine)

    def tearDown(self):
        if self.tempfile:
            os.remove(self.tempfile)
        else:
            metadata = MetaData(bind=self.db.engine)
            metadata.drop_all()

    def testIFaceZopePostgres(self):
        verifyClass(ISQLAlchemyWrapper, ZopePostgresWrapper)

    def testIModel(self):
        verifyClass(IModel, Model)

    def testSimplePopulation(self):
        db = createSAWrapper(self.dsn)
        # obtain mapper for table 'users'

        User = db.getMapper('users')
        session = db.session

        rows = session.query(User).all()
        self.assertEqual(len(rows), 0)

        session.add(User(id=1, firstname='udo', lastname='juergens'))
        session.add(User(id=2, firstname='heino', lastname='n/a'))
        session.flush()

        rows = session.query(User).order_by(User.id).all()
        self.assertEqual(len(rows), 2)
        row1 = rows[0]
        d = row1.asDict()
        self.assertEqual(d, {'firstname': 'udo',
                             'lastname': 'juergens',
                             'id': 1})

    def testMapperWithCustomModel(self):

        class myUser(MappedClassBase):
            pass

        M = Model()
        M.add('users', mapper_class=myUser)

        db = createSAWrapper(self.dsn, model=M)
        User = db.getMapper('users')
        self.assertEqual(User, myUser)

    def testCustomMapperRegister(self):
        mytable = Table(
            'mytable', self.db.metadata,
            Column('id', Integer, primary_key=True),
        )

        class MyClass:
            pass
        registry = sqlalchemy.orm.registry()
        mapper = registry.map_imperatively(MyClass, mytable)
        self.db.registerMapper(mapper, 'mymapper')

#    def testCustomMapperClassWithWrongType(self):
#
#        class myUser(object):
#            pass
#
#        M = Model()
#        self.assertRaises(TypeError, M.add, 'users', mapper_class=myUser)

    def testGetMappers(self):
        db = createSAWrapper(self.dsn)
        db.getMapper('users')
        db.getMapper('skills')
        db.getMappers('users', 'skills')

    def testModelWeirdParameters(self):
        M = Model()
        self.assertRaises(ValueError,
                          M.add,
                          'users',
                          relations=('foo', 'bar'),
                          autodetect_relations=True)

    def testModelWeirdRelationsParameters(self):
        M = Model()
        self.assertRaises(TypeError, M.add, 'users', relations=('foo'))

    def testModelNonExistingTables(self):
        M = Model()
        M.add('non_existing_table')
        db = createSAWrapper(self.dsn, model=M)
        try:
            db.getMapper('non_existing_table')
        except exc.NoSuchTableError:
            pass

    def testWrapperRegistration(self):
        wrapper = createSAWrapper(self.dsn)
        registerSAWrapper(wrapper, 'test.wrapper1')
        wrapper2 = getSAWrapper('test.wrapper1')
        self.assertEqual(wrapper, wrapper2)

    def testWrapperRegistrationFailing(self):
        createSAWrapper(self.dsn)
        self.assertRaises(ValueError, getSAWrapper, 'test.wrapperNonExistant')

    def testWrapperDoubleRegistrationFailing(self):
        wrapper = createSAWrapper(self.dsn)
        registerSAWrapper(wrapper, 'test.wrapper2')
        self.assertRaises(ValueError,
                          registerSAWrapper,
                          wrapper,
                          'test.wrapper2')

    def testWrapperDirectRegistration(self):
        wrapper = createSAWrapper(self.dsn, name='test.wrapper3')
        wrapper2 = getSAWrapper('test.wrapper3')
        self.assertEqual(wrapper, wrapper2)

    def testCheckConnection(self):
        """ Check access to low-level connection """
        db = createSAWrapper(self.dsn)
        conn = db.connection
        cursor = conn.cursor()
        cursor.execute('select * from users')
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 0)

    def testConnectionPlusSession(self):
        """ Check access to low-level connection """

        User = self.db.getMapper('users')
        session = self.db.session
        session.add(User(id=1, firstname='udo', lastname='juergens'))
        session.add(User(id=2, firstname='heino', lastname='n/a'))
        session.flush()

        conn = self.db.connection
        cursor = conn.cursor()
        cursor.execute('select * from users')
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 2)

    def testDeclarative(self):

        db = createSAWrapper(self.dsn)
        session = db.session
        metadata = db.metadata
        Base = declarative_base(metadata=metadata)

        class Foo(Base):
            __tablename__ = 'foo'

            id = Column('id', Integer, primary_key=True)
            name = Column('name', String(50))

        Base.metadata.create_all(db._engine)

        session.add(Foo(id=1, name='Andreas Jung'))
        session.add(Foo(id=2, name='Peter Becker'))
        session.flush()

        rows = session.query(Foo).all()
        self.assertEqual(len(rows), 2)

    def testDeclarativeWithModel(self):
        def getModel(metadata):

            model = Model()
            Base = declarative_base(metadata=metadata)

            class Foo(Base):
                __tablename__ = 'foo'

                id = Column('id', Integer, primary_key=True)
                name = Column('name', String(50))

            model.add('foo', mapper_class=Foo)
            Base.metadata.create_all(self.db._engine)
            return model

        db = createSAWrapper(self.dsn, model=getModel)
        session = db.session
        Foo = db.getMapper('foo')

        session.add(Foo(id=1, name='Andreas Jung'))
        session.add(Foo(id=2, name='Peter Becker'))
        session.flush()

        rows = session.query(Foo).all()
        self.assertEqual(len(rows), 2)


def test_suite():
    from unittest import TestSuite
    from unittest import makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(WrapperTests))
    return suite
