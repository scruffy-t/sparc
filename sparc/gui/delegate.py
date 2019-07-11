"""

"""
# system modules
import collections

# 3rd party modules
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

# sparc modules
from sparc.core import *
from .settings import DEFAULT_SETTINGS as SETTINGS
from .model import ParamModel

__all__ = ['ParamModelDelegate']


class ParamModelDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None):
        QtWidgets.QStyledItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        """
        """
        model = index.model()
        assert isinstance(model, ParamModel), 'ParamModelDelegate can only be used with ParamModel!'
        node = model.nodeFromIndex(index)

        # NOTE: we don't need to check whether node.is_editable()
        # because only editable nodes will request this method

        if model.isValue(index):

            # the default node value type is str
            node_type = node.type() or str
            validator = node.validator()

            # if node is an expression, we simply return a line edit
            if node.is_expression():
                editor = QtWidgets.QLineEdit(parent)
                editor.setText(node.raw_value())
                return editor

            # if validator is a Collection, the delegate is a QComboBox
            # Collection := limited number of known choices
            if isinstance(validator, collections.Collection):

                if node_type == QtGui.QColor:
                    # TODO: implement color combo box
                    editor = QtWidgets.QComboBox(parent)
                    for row, valid_value in enumerate(validator):
                        editor.addItem('', valid_value)
                        editor.setItemData(row, valid_value, QtCore.Qt.BackgroundColorRole)
                    editor.setCurrentText(node.value().name())
                    return editor
                else:
                    editor = QtWidgets.QComboBox(parent)
                    for valid_value in validator:
                        editor.addItem(str(valid_value), valid_value)
                    editor.setCurrentText(str(node.value()))
                    return editor

            if node_type is str:
                editor = QtWidgets.QLineEdit(parent)
                editor.setText(str(node.value()))
                return editor
            if node_type is int:
                editor = QtWidgets.QSpinBox(parent)
                if isinstance(validator, Interval):
                    # TODO: make sure spinbox can handle min and max
                    editor.setRange(validator.min, validator.max)
                else:
                    # TODO: replace numpy code
                    maxi = np.iinfo(np.int32).max
                    editor.setRange(-maxi, maxi)
                editor.setValue(node.value())
                return editor
            if node_type is float:
                editor = QtWidgets.QDoubleSpinBox(parent)
                editor.setDecimals(SETTINGS.value('decimals'))
                if isinstance(validator, Interval):
                    # TODO: make sure spinbox can handle min and max
                    editor.setRange(validator.min, validator.max)
                else:
                    # TODO: replace numpy code
                    maxf = np.finfo(np.float32).max
                    editor.setRange(-maxf, maxf)
                editor.setValue(node.value())
                return editor
            if node_type is list:
                # TODO: implement list editor
                editor = QtWidgets.QLineEdit(parent)
                editor.setText(str(node.value()))
                return editor
            if node_type is QtGui.QColor:
                editor = QtWidgets.QColorDialog(node.value(), parent)
                return editor

        return QtWidgets.QStyledItemDelegate.createEditor(self, parent, option, index)

    def paint(self, painter, option, index):
        QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)

    def setEditorData(self, editor, index):
        QtWidgets.QStyledItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        node = model.nodeFromIndex(index)

        if isinstance(editor, QtWidgets.QComboBox):
            # get user data (with correct type) instead of str
            model.setData(index, editor.currentData(), QtCore.Qt.EditRole)
        elif isinstance(editor, QtWidgets.QColorDialog):
            if editor.result() == QtWidgets.QDialog.Accepted:
                model.setData(index, editor.selectedColor(), QtCore.Qt.EditRole)
        else:
            QtWidgets.QStyledItemDelegate.setModelData(self, editor, model, index)
