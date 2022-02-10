
from future.utils import PY3

if PY3:
    from urllib.robotparser import *
else:
    __future_module__ = True
    from urllib.robotparser import *
