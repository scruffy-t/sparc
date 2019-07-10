HAVE_QT = False

try:
    import PyQt5
    HAVE_QT = True
except ImportError:
    HAVE_QT = False

__all__ = ['HAVE_QT']

if HAVE_QT:
    from .delegate import ParamModelDelegate
    from .model import ParamModel
    from .settings import *
    from .widgets import ParamTableWidget
    from sparc.gui.widgets.tree import ParamTreeWidget
    __all__ = __all__.extend(['ParamModelDelegate', 'ParamModel', 'ParamTableWidget', 'ParamTreeWidget'])
