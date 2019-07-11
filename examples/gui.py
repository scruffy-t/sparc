import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog

from sparc.core import *
from sparc.gui import ParamTreeWidget


class MainWindow(QMainWindow):

    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        QMainWindow.__init__(self, parent, flags)

        p = ParamGroupNode('set')
        p.add_children(tuple([
            {'name': 'x', 'value': -1.0, 'type': float},
            {'name': 'y', 'value': 2.0, 'type': float},
            {'name': 'z', 'value': '=(x+y)**0.5', 'type': float},
            {'name': 'const_check', 'value': True, 'type': bool, 'editable': False},
            {'name': 'check', 'value': True, 'type': bool, 'editable': True},
            {'name': 'color', 'value': Qt.red, 'type': QColor},
            {'name': 'color_combo', 'value': Qt.red, 'type': QColor, 'validator': [QColor(Qt.red), QColor(Qt.black)]},
            {'name': 'group'},
            {'name': 'group.first', 'value': 23.4, 'type': float},
            {'name': 'group.second', 'value': 45.3, 'type': float},
            {'name': 'group.result', 'value': '=first+second', 'type': float},
            {'name': 'group.subgroup'},
            {'name': 'group.subgroup.x', 'value': 3, 'type': int},
            {'name': 'group.subgroup.y', 'value': '=x+extern'}
        ]))

        self.widget = ParamTreeWidget(p)
        self.widget.setExpressionContext({'extern': 34})
        self.setCentralWidget(self.widget)

        file_menu = self.menuBar().addMenu('File')
        file_menu.addAction('&Load', self.widget.load)
        file_menu.addAction('&Save', self.widget.save)


def main():

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
