
from future.utils import PY3

if PY3:
    from http.cookiejar import *
else:
    __future_module__ = True
    from http.cookiejar import *
