from unittest import TestCase
from sparc.core import *


class TestExpressionNode(TestCase):

    def test_init(self):

        p = ParamGroupNode('set')
        p.add_child('m', 5.0, float)
        p.add_child('a', 2.0, float)
        p.add_child('A', 4.0, float)
        p.add_child('F', '=m*a')
        p.add_child('Sigma', '=F/A')
        p.add_child('l', '=A**0.5')
        p.add_child('extern', '=A * F + x')

        self.assertEqual(p.child('F').value(), 10.0)
        self.assertEqual(p.child('Sigma').value(), 2.5)
        self.assertEqual(p.child('l').value(), 2.0)
        self.assertEqual(p.child('extern').value(x=2, F=34), 42.0)

        with self.assertRaises(NameError):
            p.child('extern').value()
