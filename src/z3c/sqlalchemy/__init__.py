##########################################################################
# z3c.sqlalchemy - A SQLAlchemy wrapper for Python/Zope
#
# (C) Zope Corporation and Contributor
# Written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
# and ZOPYX Ltd. & Co. KG, Tuebingen, Germany
##########################################################################


from util import *
from model import Model

try:
    from sqlalchemy.orm import sessionmaker
except ImportError:
    raise ImportError('z3c.sqlalchemy requires SQLAlchemy 0.4 or higher')
