##########################################################################
# z3c.sqlalchemy - A SQLAlchemy wrapper for Python/Zope
#
# (C) Zope Corporation and Contributor
# Written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
# and ZOPYX Ltd. & Co. KG, Tuebingen, Germany
##########################################################################

import os

from setuptools import find_packages
from setuptools import setup


HERE = os.path.abspath(os.path.dirname(__file__))


def _read_file(filename):
    with open(os.path.join(HERE, filename)) as f:
        return f.read()


README = _read_file('README.rst')
CHANGES = _read_file('CHANGES.rst')
version = '2.1.1'


setup(name='z3c.sqlalchemy',
      version=version,
      url='https://github.com/zopefoundation/z3c.sqlalchemy',
      project_urls={
          'Issue Tracker': ('https://github.com/zopefoundation/'
                            'z3c.sqlalchemy/issues'),
          'Sources': 'https://github.com/zopefoundation/z3c.sqlalchemy',
      },
      license='ZPL 2.1',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      maintainer='Zope Foundation and Contributors',
      maintainer_email='zope-dev@zope.dev',
      description='A SQLAlchemy wrapper for Zope',
      long_description='\n\n'.join([README, CHANGES]),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Operating System :: OS Independent',
          'Framework :: Zope',
          'Framework :: Zope :: 3',
          'Framework :: Zope :: 4',
          'Framework :: Zope :: 5',
          'Programming Language :: Python',
          'Topic :: Database :: Front-Ends',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
      ],
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      namespace_packages=['z3c'],
      python_requires='>=3.7',
      install_requires=[
          'setuptools',
          'SQLAlchemy>=1.4',
          'zope.sqlalchemy>=1.2.0',
          'zope.component',
          'zope.interface',
          'zope.testing',
          'zope.schema',
      ],
      extras_require=dict(test=['zope.testing']))
