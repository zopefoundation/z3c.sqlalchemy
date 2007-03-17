from setuptools import setup, find_packages

setup(name='z3c.sqlalchemy',
      version='trunk',
      author='Andreas Jung',
      author_email='info@zopyx..com',
      url='https://svn.zope.org.repos/main',
      description="""SQLAlchemy integration into Zope 2 and Zope 3""",
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
