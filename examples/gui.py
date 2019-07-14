# gui.py

# system modules
import sys

# 3rd party modules
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QTreeView

# sparc modules
from sparc import __version__, ParamGroupNode
from sparc.gui import ParamModel, ParamDelegate


def main():

    p = ParamGroupNode('set')

    p.add_children([
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
    ])

    app = QApplication(sys.argv)
    app.setApplicationDisplayName(f'sparc (v{__version__})')

    model = ParamModel(p)
    model.setExpressionContext({'extern': 34})

    view = QTreeView()
    view.setModel(model)
    view.setItemDelegate(ParamDelegate(view))
    view.setWindowTitle(app.applicationDisplayName())

    view.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
