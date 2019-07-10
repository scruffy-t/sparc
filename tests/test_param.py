from unittest import TestCase
from sparc.core import ParamNode, Interval

import random


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
        self.assertEqual(p.is_valid_value(random.randint(-10000, 10000)), True)

    def test_values(self):
        p = ParamNode('x', 0, int, validator=Interval(-1, +1, (Interval.Closed, Interval.Open)))
        self.assertEqual(p.is_valid_value(-1), False)
        self.assertEqual(p.is_valid_value(+1), True)
