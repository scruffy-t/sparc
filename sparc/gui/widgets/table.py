from PyQt5 import QtCore, QtGui, QtWidgets


class ParamTableWidget(QtWidgets.QTableWidget):

    def __init__(self, parent=None):
        QtWidgets.QTableWidget.__init__(self, parent)
        self._keys = ()
        self.verticalHeader().hide()

    def setParamKeys(self, keys, units=()):
        self.clear()
        self.setColumnCount(len(keys))
        self._keys = keys

        units = list(units) + ['-' for _ in range(len(keys)-len(units))]
        labels = ['%s [%s]' % (key.replace('_', ' ').title(), unit) for key, unit in zip(keys, units)]
        QtWidgets.QTableWidget.setHorizontalHeaderLabels(self, labels)

        # TODO: repopulate table

    def paramKeys(self):
        return self._keys

    def addParamSet(self, param):
        row = self.rowCount()
        self.setRowCount(row + 1)
        for column, key in enumerate(self.paramKeys()):
            value = param[key].value()
            item = QtWidgets.QTableWidgetItem(str(value))
            self.setItem(row, column, item)

    def addParamSets(self, params):
        for param in params:
            self.addParamSet(param)
