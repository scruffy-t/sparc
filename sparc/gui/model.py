from PyQt4 import QtCore, QtGui
from sparc.core import *

import pint


class ParamModel(QtCore.QAbstractItemModel):

    def __init__(self, param, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self._root = ParamSet('root')
        self._root.add_child(param)

    def columnCount(self, parentIndex=None, *args, **kwargs):
        return 3

    def data(self, index, role=None):
        if not index.isValid():
            return None

        node = self.nodeFromIndex(index)
        column = index.column()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if column == 0:
                return node.display_name()
            elif column == 1 and isinstance(node, AbstractParam):
                if role == QtCore.Qt.EditRole and isinstance(node, DependentParam):
                    return node.expr()
                try:
                    return node.value()
                except Exception as e:
                    return e.message
            elif column == 2 and isinstance(node, AbstractParam):
                try:
                    return node.unit()
                except pint.DimensionalityError as e:
                    return e.message

        elif role == QtCore.Qt.TextAlignmentRole:
            if column != 0:
                return QtCore.Qt.AlignHCenter

        elif role == QtCore.Qt.BackgroundColorRole:
            if isinstance(node, DependentParam) and not node.is_valid():
                return QtGui.QBrush(QtCore.Qt.red)

        return None

    def flags(self, index):
        node = self.nodeFromIndex(index)
        f = QtCore.QAbstractItemModel.flags(self, index)

        if index.column() != 0 and isinstance(node, AbstractParam):
            return f | QtCore.Qt.ItemIsEditable
        return f

    def hasChildren(self, parentIndex=None, *args, **kwargs):
        node = self.nodeFromIndex(parentIndex)
        if isinstance(node, AbstractParam):
            return False
        return True

    def headerData(self, section, orientation, role=None):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return ['Name', 'Value', 'Unit'][section]
        return None

    def index(self, row, column, parentIndex=None, *args, **kwargs):
        if not self.hasIndex(row, column, parentIndex):
            return QtCore.QModelIndex()

        parent = self.nodeFromIndex(parentIndex)
        return self.createIndex(row, column, parent.child(row))

    def nodeFromIndex(self, index):
        return index.internalPointer() if index.isValid() else self._root

    def parent(self, index=None):
        if index.isValid():
            parent = self.nodeFromIndex(index).parent()
            if parent != self._root:
                return self.createIndex(parent.index(), 0, parent)
        return QtCore.QModelIndex()

    def rowCount(self, parentIndex=None, *args, **kwargs):
        return len(self.nodeFromIndex(parentIndex))

    def setData(self, index, value, role=None):
        if not index.isValid():
            return None

        value = value.toPyObject()
        node = self.nodeFromIndex(index)

        if role == QtCore.Qt.EditRole:
            if index.column() == 0:
                # TODO: Disabled due to DependendParam issues
                # we have to be careful here because we might invalidate existing
                # DependendParams by changing a variable name
                # node.setName(unicode(value))
                # return True
                pass
            # set Param value
            if index.column() == 1 and isinstance(node, Param):
                if node.is_valid_value(value):
                    node.set_value(value)
                    return True
                return False
            # set DependendParam expression
            if index.column() == 1 and isinstance(node, DependentParam):
                value = str(value)
                if node.is_valid_expr(value):
                    node.set_expr(value)
                    return True
                return False
            # set Param unit
            if index.column() == 2 and isinstance(node, Param):
                node.set_unit(value)
                return True

        return False
