import pickle

from PyQt5.QtWidgets import *

from sparc.gui.model import ParamModel
from sparc.gui.delegate import ParamModelDelegate


class ParamTreeWidget(QWidget):

    def __init__(self, root=None, parent=None):
        QWidget.__init__(self, parent)

        self.view = QTreeView(self)
        self.model = ParamModel(root, self)
        self.view.setModel(self.model)
        self.view.setItemDelegate(ParamModelDelegate(self))

        self.view.setEditTriggers(
            QAbstractItemView.SelectedClicked | QAbstractItemView.EditKeyPressed
        )

        self.toolbar = QToolBar(parent=self)
        # TODO: fill toolbar with tools
        self.toolbar.addAction('Add')
        self.toolbar.addAction('Remove')
        self.toolbar.addAction('Save', self.save)
        self.toolbar.addAction('Load', self.load)

        self.statusbar = QStatusBar(parent=self)
        self.statusbar.setSizeGripEnabled(parent is None)
        # TODO: add other messages?
        self.model.errorMessage.connect(self.statusbar.showMessage)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.view)
        layout.addWidget(self.statusbar)
        self.setLayout(layout)

    def save(self):
        filename = QFileDialog.getSaveFileName(self, 'Save Pickle', '', 'Pickle (*.pcl)')[0]
        if filename != '':
            with open(filename, 'wb') as param_file:
                # TODO: add error message to statusbar if this fails
                pickle.dump(self.model.root(), param_file)

    def load(self):
        filename = QFileDialog.getOpenFileName(self, 'Load Pickle', '', 'Pickle (*.pcl)')[0]
        if filename != '':
            with open(filename, 'rb') as param_file:
                # TODO: add error message to statusbar if this fails
                self.model.setRoot(pickle.load(param_file))

    def root(self):
        return self.model.root()

    def setExpressionContext(self, context):
        self.model.setExpressionContext(context)

    def setRoot(self, node):
        self.model.setRoot(node)
