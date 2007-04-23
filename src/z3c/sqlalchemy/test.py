from sqlalchemy import *
from z3c.sqlalchemy import createSQLAlchemyWrapper, Model
from z3c.sqlalchemy.mapper import MappedClassBase 

dsn = 'postgres://postgres:postgres@cmsdb/Toolbox2Test'

class HierarchyNode(MappedClassBase):
    pass

# FIX THIS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
e = create_engine(dsn)
metadata = BoundMetaData(e)
# FIX THIS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


HierarchyTable = Table('hierarchy', metadata,
                       Column('parentid', Integer, ForeignKey('hierarchy.id')),
                       autoload=True)


mapper(HierarchyNode, HierarchyTable, properties={
    'children' : relation(
                    HierarchyNode,
                    primaryjoin=HierarchyTable.c.parentid==HierarchyTable.c.id,
                    cascade="all",
                    backref=backref("parent", remote_side=[HierarchyTable.c.id])
                 ),
    'parent' : relation(
                    HierarchyNode,
                    primaryjoin=HierarchyTable.c.parentid==HierarchyTable.c.id,
                    remote_side=[HierarchyTable.c.id],
                    uselist=False,
                 ),
    }
)

m = Model()
m.add('hierarchy', table=HierarchyTable, mapper_class=HierarchyNode)





wrapper = createSQLAlchemyWrapper(dsn, model=m)
session = wrapper.session


H = wrapper.getMapper('hierarchy')

print H
rows = session.query(H).select_by(H.c.id==8)
print rows[0].children
