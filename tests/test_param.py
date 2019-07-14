from unittest import TestCase
from sparc.core import ParamNode, ParamGroupNode, Interval


class TestParamNode(TestCase):

    def test_init(self):
        p = ParamNode('test', 34, str, True, None)
        self.assertEqual(p.type(), str)
        self.assertEqual(p.value(), '34')

        p = ParamNode('test', 34.0, int, False, Interval(0, 100))
        self.assertEqual(p.value(), 34)

        with self.assertRaises(AttributeError):
            p.set_value(10)

        p.set_editable(True)
        with self.assertRaises(ValueError):
            p.set_value(-20)

        p = ParamNode('test', 'a', str, True, ['a', 'b', 'c'])
        self.assertEqual(p.value(), 'a')

        p.set_value('b')
        p.set_value('c')
        with self.assertRaises(ValueError):
            p.set_value('d')

    def test_name(self):
        p = ParamNode(u'Überläufer', 0, int)
        self.assertEqual(p.is_editable(), True)

    def test_editable(self):
        p = ParamNode('x', 0, int)
        self.assertEqual(p.is_editable(), True)

    def test_values(self):
        p = ParamNode('x', 0, int, validator=Interval(-1, +1, (Interval.Closed, Interval.Open)))
        with self.assertRaises(ValueError):
            p.set_value(-1)

        with self.assertRaises(ValueError):
            p.set_value('Hello World')

    def test_expression(self):
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

        # context F takes precedence over sibling F!
        self.assertEqual(p.child('extern').value(context={'x': 2, 'F': 20.0}), 82.0)

        with self.assertRaises(NameError):
            p.child('extern').value()
