
from future.utils import PY3

if PY3:
    from builtins import *
else:
    __future_module__ = True
    from builtins import *
    # Overwrite any old definitions with the equivalent future.builtins ones:
    from future.builtins import *
