from PyQt4 import QtCore, QtGui


class ParamTableWidget(QtGui.QTableWidget):

    def __init__(self, parent=None):
        QtGui.QTableWidget.__init__(self, parent)
        self._keys = ()
        self.verticalHeader().hide()

    def setParamKeys(self, keys, units=()):
        self.clear()
        self.setColumnCount(len(keys))
        self._keys = keys

        units = list(units) + ['-' for _ in range(len(keys)-len(units))]
        labels = ['%s [%s]' % (key.replace('_', ' ').title(), unit) for key, unit in zip(keys, units)]
        QtGui.QTableWidget.setHorizontalHeaderLabels(self, labels)

        # TODO: repopulate table

    def paramKeys(self):
        return self._keys

    def addParamSet(self, param):
        row = self.rowCount()
        self.setRowCount(row + 1)
        for column, key in enumerate(self.paramKeys()):
            text = param[key].value
            item = QtGui.QTableWidgetItem(str(text))
            self.setItem(row, column, item)

    def addParamSets(self, params):
        for param in params:
            self.addParamSet(param)