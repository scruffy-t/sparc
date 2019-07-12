import pickle

from PyQt5 import QtCore, QtGui

from sparc.core import *
from .settings import DEFAULT_SETTINGS as SETTINGS

__all__ = ['ParamModel']


class ParamItem(object):

    def __init__(self, node):
        if not isinstance(node, (ParamNode, ParamGroupNode)):
            raise TypeError('node must be ParamNode or ParamGroupNode instance')
        if isinstance(node, ParamNode) and node.is_unbound():
            raise TypeError('ParamModel does not support unbound ParamNode instances')
        self.node = node

    def data(self, column, role, context=None):

        if role == QtCore.Qt.CheckStateRole:
            if column == 1:  # value column
                if not isinstance(self.node, ParamNode):
                    return None

                if self.node.type() is bool:
                    return QtCore.Qt.Checked if self.node.value() else QtCore.Qt.Unchecked

        if role == QtCore.Qt.DisplayRole:
            if column == 0:  # name column
                return self.node.display_name()
            elif column == 1:  # value column
                if not isinstance(self.node, ParamNode):
                    return None

                try:
                    value = self.node.value(context=context)
                except Exception as e:
                    value = str(e)

                value_type = type(value)

                if value_type == QtGui.QColor:
                    return None
                elif value_type is float:
                    return '{v:.{d}f}'.format(v=value, d=SETTINGS.value('decimals'))
                elif value_type is not bool:
                    return str(value)

        elif role == QtCore.Qt.EditRole:
            if column == 0:
                return self.node.display_name()
            elif column == 1:
                if isinstance(self.node, ParamGroupNode):
                    return None
                return self.node.raw_value()

        elif role == QtCore.Qt.TextAlignmentRole:
            if column == 1:
                return QtCore.Qt.AlignLeft

        elif role == QtCore.Qt.BackgroundColorRole:
            if isinstance(self.node, ParamGroupNode):
                return QtGui.QBrush(QtCore.Qt.lightGray)
            elif column == 1 and self.node.type() == QtGui.QColor:
                return QtGui.QBrush(self.node.value())

        elif role == QtCore.Qt.ForegroundRole:
            if isinstance(self.node, ParamNode) and not self.node.is_editable():
                return QtGui.QColor(QtCore.Qt.darkGray)

        return None

    def setData(self, column, value, role):

        if not isinstance(self.node, ParamNode):
            return False

        if role == QtCore.Qt.EditRole:

            # set name
            if column == 0:
                # --- Disabled due to ExpressionParamNode issues ---
                # we have to be careful here because we might invalidate an existing
                # ExpressionParamNode by changing a variable name
                # node.setName(unicode(value))
                # return True
                pass

            # set value
            elif column == 1:
                try:
                    self.node.set_value(value)
                except Exception:
                    return False
                return True

        elif role == QtCore.Qt.CheckStateRole:

            value = True if value == QtCore.Qt.Checked else False
            try:
                self.node.set_value(value)
            except Exception:
                return False
            return True

        return False


class ParamModel(QtCore.QAbstractItemModel):

    # TODO: Catch all exceptions and emit them as errorMessage
    errorMessage = QtCore.pyqtSignal(str)
    valueChanged = QtCore.pyqtSignal(str)

    def __init__(self, root=None, parent=None):
        """
        """
        QtCore.QAbstractItemModel.__init__(self, parent)
        self._context = {}
        self._root = root or ParamGroupNode('root')

    def columnCount(self, parentIndex=None, *args, **kwargs):
        """
        """
        if parentIndex.isValid() and parentIndex.column() != 0:
            return 0
        return 2

    def data(self, index, role=None):
        """
        """
        if not index.isValid():
            return None

        node = self.nodeFromIndex(index)
        item = ParamItem(node)

        return item.data(index.column(), role, context=self._context)

    def flags(self, index):
        """
        """
        f = QtCore.QAbstractItemModel.flags(self, index)
        if not index.isValid():
            return f

        if not self.isEditable(index):
            return f

        node = self.nodeFromIndex(index)
        assert isinstance(node, ParamNode)

        if node.type() == bool:
            return f | QtCore.Qt.ItemIsUserCheckable
        else:
            return f | QtCore.Qt.ItemIsEditable

    def headerData(self, section, orientation, role=None):
        """
        """
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return ['Name', 'Value'][section]
        return None

    def index(self, row, column, parent=None, *args, **kwargs):
        """

        Parameters
        ----------
        row: int
        column: int
        parent: QModelIndex
        """
        if parent.isValid() and parent.column() != 0:
            return QtCore.QModelIndex()

        parent_node = self.nodeFromIndex(parent)
        return self.createIndex(row, column, parent_node.child(row))

    def isName(self, index):
        return index.column() == 0

    def isValue(self, index):
        return index.column() == 1

    def isGroup(self, index):
        return isinstance(self.nodeFromIndex(index), ParamGroupNode)

    def isLeaf(self, index):
        return isinstance(self.nodeFromIndex(index), ParamNode)

    def isEditable(self, index):
        if not self.isLeaf(index):
            return False

        node = self.nodeFromIndex(index)
        assert isinstance(node, ParamNode)

        return node.is_editable()

    def load(self, filename, binary=True):
        if binary:
            with open(filename, 'rb') as spc:
                root = pickle.load(spc)
                self.setRoot(root)
        else:
            with open(filename, 'r') as spj:
                root = load(spj)
                self.setRoot(root)

    def nodeFromIndex(self, index):
        """
        """
        return index.internalPointer() if index.isValid() else self._root

    def parent(self, index=None):
        """
        """
        if index.isValid():
            parent = self.nodeFromIndex(index).parent()
            if parent is not None and parent != self._root:
                return self.createIndex(parent.index(), 0, parent)
        return QtCore.QModelIndex()

    def root(self):
        """
        """
        return self._root

    def rowCount(self, parent=None, *args, **kwargs):
        """

        Parameters
        ----------
        parent: QModelIndex
        """
        if parent.isValid() and parent.column() != 0:
            return 0
        node = self.nodeFromIndex(parent)
        if isinstance(node, ParamNode):
            return 0
        return node.child_count()

    def save(self, filename, binary=True):
        if binary:
            with open(filename, 'wb') as spc:
                pickle.dump(self.root(), spc)
        else:
            with open(filename, 'w') as spj:
                dump(self.root(), spj, indent=2)

    def setExpressionContext(self, context):
        self._context = context
        # TODO: init re-evaluation of expression nodes

    def setData(self, index, value, role=None):
        """
        """
        if not index.isValid():
            return False

        node = self.nodeFromIndex(index)
        item = ParamItem(node)

        try:
            success = item.setData(index.column(), value, role)
        except ValueError as e:
            self.errorMessage.emit(str(e))
            success = False

        if role in (QtCore.Qt.EditRole, QtCore.Qt.CheckStateRole) and success:
            self.valueChanged.emit(node.absolute_name())

        return success

    def setRoot(self, root):
        """
        """
        self.beginResetModel()
        self._root = root
        self.endResetModel()
