from unittest import TestCase
from sparc.core import Param, ParamSet
from sparc.gui.widgets import ParamTableWidget

from PyQt4 import QtGui

import random


class TestParamTable(TestCase):

    def test_init(self):

        # app = QtGui.QApplication([])
        #
        # sparc = []
        # for i in range(100):
        #     p = ParamSet('set')
        #     p.add('x', random.randint(-100, 100))
        #     p.add('y', random.randint(-100, 100))
        #     p.add('z', random.randint(-100, 100))
        #     sparc.append(p)
        #
        # table = ParamTableWidget()
        # table.setParamKeys(['x', 'y', 'z'], units=['m', 'm'])
        # table.addParamSets(sparc)
        # table.show()
        #
        # return app.exec_()

        pass
