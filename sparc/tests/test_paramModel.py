from unittest import TestCase
from sparc.core import *
from sparc.gui import *

from PyQt4 import QtCore, QtGui


class TestParamModel(TestCase):

    def test_model_init(self):

        p = ParamSet('set')
        p.add_child('x', -1.0, unit='m')
        p.add_child('y', 2.0, unit='s')
        p.add_child('z', expr='(x+y)**0.5')

        self.assertEqual(p.child('x').index(), 0)
        self.assertEqual(p.child('y').index(), 1)
        self.assertEqual(p.child('z').index(), 2)

        self.assertEqual(p.child(0), p.child('x'))
        self.assertEqual(p.child(1), p.child('y'))
        self.assertEqual(p.child(2), p.child('z'))

        self.assertEqual(p.child('x').index(), p.index_of_child('x'))
        self.assertEqual(p.child('y').index(), p.index_of_child('y'))
        self.assertEqual(p.child('z').index(), p.index_of_child('z'))

        model = ParamModel(p)

        app = QtGui.QApplication([])
        view = QtGui.QTreeView()
        view.setModel(model)

        view.show()
        return app.exec_()
