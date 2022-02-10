from future.utils import PY3

if PY3:
    from http.client import *
else:
    from http.client import *
    from http.client import HTTPMessage
    __future_module__ = True
