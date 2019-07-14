import warnings

try:
    import PyQt5
    HAVE_QT = True
except ImportError:
    HAVE_QT = False
    warnings.warn('sparc.gui requires PyQt5 which is not installed.\n'
                  'You can install PyQt5 in the terminal with\n'
                  'pip install PyQt5')

if HAVE_QT:
    from .delegate import *
    from .model import *
    from .settings import *
    from .types import *
