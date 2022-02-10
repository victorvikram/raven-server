

from future.utils import PY3

if PY3:
    from dbm.ndbm import *
else:
    __future_module__ = True
    from dbm.ndbm import *
