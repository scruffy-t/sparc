from PyQt5.QtWidgets import *

from sparc.gui import ParamModel, ParamModelDelegate

__all__ = ['ParamTreeWidget']


class ParamTreeWidget(QWidget):

    def __init__(self, root=None, parent=None):
        QWidget.__init__(self, parent)

        self._view = QTreeView(self)
        self._model = ParamModel(root, self)
        self._view.setModel(self._model)
        self._view.setItemDelegate(ParamModelDelegate(self))

        self._view.setEditTriggers(
            QAbstractItemView.SelectedClicked | QAbstractItemView.EditKeyPressed
        )

        self._statusbar = QStatusBar(parent=self)
        self._statusbar.setSizeGripEnabled(parent is None)
        # TODO: add other messages?
        self._model.errorMessage.connect(self._statusbar.showMessage)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._view)
        layout.addWidget(self._statusbar)
        self.setLayout(layout)

    def model(self):
        return self._model

    def save(self):
        filename, filter = QFileDialog.getSaveFileName(self, 'Save Model', filter='JSON (*.json);;Pickle (*.pcl)')
        if filename != '':
            binary = filter.startswith('Pickle')
            self._model.save(filename, binary=binary)

    def load(self):
        filename, filter = QFileDialog.getOpenFileName(self, 'Load Model', filter='JSON (*.json);;Pickle (*.pcl)')
        if filename != '':
            binary = filter.startswith('Pickle')
            self._model.load(filename, binary=binary)

    def root(self):
        return self._model.root()

    def setExpressionContext(self, context):
        self._model.setExpressionContext(context)

    def setRoot(self, node):
        self._model.setRoot(node)

