from unittest import TestCase
from sparc.core import *


class TestParamGroup(TestCase):

    def test_add(self):

        group = ParamGroup('group')
        group.add('c0', 0.0)
        group.add('c1', 1.0)
        group.add('c2', 2.0)
        group.add('c3', 3.0)

        group.add_child('r0')
        group.add_child('r1')
        group.add_child('r2')

    def test_value(self):

        group = ParamGroup('group')
        group.add('c0', 0.0)
        group.add('c1', 1.0)
        group.add('c2', 2.0)
        group.add('c3', 3.0)

        group.add_child('r0')

        self.assertEqual(group.child('r0').child('c0').value(), 0.0)
        self.assertEqual(group.child('r0').child('c1').value(), 1.0)
        self.assertEqual(group.child('r0').child('c2').value(), 2.0)
        self.assertEqual(group.child('r0').child('c3').value(), 3.0)
