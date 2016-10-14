try:
    import PyQt4
    HAVE_PYQT4 = True
except ImportError:
    HAVE_PYQT4 = False

from .model import ParamModel

__all__ = ['ParamModel']
