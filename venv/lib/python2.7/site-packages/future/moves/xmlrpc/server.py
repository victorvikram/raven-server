
from future.utils import PY3

if PY3:
    from xmlrpc.server import *
else:
    from xmlrpc.client import *
