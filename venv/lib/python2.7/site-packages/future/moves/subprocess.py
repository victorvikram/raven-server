
from future.utils import PY2, PY26

from subprocess import *

if PY2:
    __future_module__ = True
    from subprocess import getoutput, getstatusoutput

if PY26:
    from future.backports.misc import check_output
