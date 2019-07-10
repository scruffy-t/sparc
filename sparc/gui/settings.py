from PyQt5 import QtCore
from PyQt5 import QtGui

__all__ = ['DEFAULT_SETTINGS', 'print_Qt_config']

DEFAULT_SETTINGS = QtCore.QSettings('Nutshell', 'sparc')
DEFAULT_SETTINGS.setValue('decimals', 5)


def print_Qt_config():
    import sys

    print("Python sys.executable:\n\t%s" % sys.executable)
    print("Python sys.path:\n\t%s" % "\n\t".join(sys.path))
    print('Qt5 Libraries path:\n\t%s' % QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.LibrariesPath))
    print('Qt5 Library Executables path:\n\t%s' % QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.LibraryExecutablesPath))
    print('Qt5 Binaries path:\n\t%s' % QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.BinariesPath))
    print('Qt5 Data path:\n\t%s' % QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.DataPath))
    print('Qt5 Imports path:\n\t%s' % QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.ImportsPath))
    print('Qt5 Plugins path:\n\t%s' % QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.PluginsPath))
    print('Qt5 Settings path:\n\t%s' % QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.SettingsPath))
    print('Qt5 Prefix path:\n\t%s' % QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.PrefixPath))
    print("Qt5 image read support:\n\t%s" % ', '.join([str(format).lower() for format in QtGui.QImageReader.supportedImageFormats()]))
