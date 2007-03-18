from setuptools import setup, find_packages

setup(name='z3c.sqlalchemy',
      version='0.1',
      author='Andreas Jung',
      author_email='info@zopyx..com',
      url='svn://svn.zope.org.repos/main/z3c.sqlalchemy/tags/0.1',
      description=open('src/z3c/sqlalchemy/README.txt').read(),
      license='ZPL 2.1',

      packages=find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data = True,
      zip_safe=False,
      install_requires=['setuptools',
                        'SQLAlchemy',
                        'zope.component',
                        'zope.interface',
                        'zope.schema',
                       ],
      extras_require = dict(test=['pysqlite']))
