##########################################################################
# z3c.sqlalchemy - A SQLAlchemy wrapper for Python/Zope
#
# (C) Zope Corporation and Contributor
# Written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
# and ZOPYX Ltd. & Co. KG, Tuebingen, Germany
##########################################################################


from setuptools import setup, find_packages

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Zope Public License',
    'Operating System :: OS Independent',
    'Framework :: Zope2',
    'Framework :: Zope3',
    'Programming Language :: Python',
    'Topic :: Database :: Front-Ends',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

version = '1.3.7'

desc = open('README.txt').read().strip()
changes = open('CHANGES.txt').read().strip()

long_description = desc + '\n\nChanges\n=======\n\n'  + changes


setup(name='z3c.sqlalchemy',
      version=version,
      license='ZPL (see LICENSE.txt)',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      maintainer='Andreas Jung',
      maintainer_email='info@zopyx.com',
      classifiers=CLASSIFIERS,
      url='http://svn.zope.org/z3c.sqlalchemy/tags/%s' % version,
      description='A SQLAlchemy wrapper for Zope 2 and Zope 3',
      long_description=long_description,
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      namespace_packages=['z3c'],
      install_requires=['setuptools',
                        'SQLAlchemy',
                        'zope.sqlalchemy',
                        'zope.component',
                        'zope.interface',
                        'zope.schema',
                        'zope.testing',
                       ],
      extras_require=dict(test=['pysqlite', 'zope.testing']))
