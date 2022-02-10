
from future.utils import PY3

if PY3:
    from pickle import *
else:
    __future_module__ = True
    try:
        from pickle import *
    except ImportError:
        from pickle import *
