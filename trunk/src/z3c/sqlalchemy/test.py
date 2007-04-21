from haufe.sqlalchemy import createSQLAlchemyWrapper, Model

class Format(object):
    pass

m = Model({'name' : 'format', 'autodetect_relations' : True, 'mapper_class' : Format},
          {'name' : 'medium', 'autodetect_relations' : True})



w = createSQLAlchemyWrapper('postgres://postgres:postgres@cmsdb/MedienDB', model=m)

print w
f = w.getMapper('format')
m = w.getMapper('medium')

session = w.session
for row in session.query(f).select():
    print row.versionfiles
