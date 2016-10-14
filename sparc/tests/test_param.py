# --*-- encoding: utf-8 --*--

from unittest import TestCase
from sparc.core import Param, Interval

import random


class TestParam(TestCase):

    # TODO: Add tests for other param types such as: str, enum, etc.

    def test_name(self):
        p = Param(u'Überläufer', 0, int)
        self.assertEqual(p.is_editable(), True)

    def test_editable(self):
        p = Param('x', 0, int)
        self.assertEqual(p.is_editable(), True)
        self.assertEqual(p.is_valid_value(random.randint(-10000, 10000)), True)

    def test_values(self):
        p = Param('x', 0, int, values=Interval(-1, +1, (Interval.Closed, Interval.Open)))
        self.assertEqual(p.is_valid_value(-1), False)
        self.assertEqual(p.is_valid_value(+1), True)

    def test_units(self):
        p = Param('x', 1.0, unit='m')
        p.convert_to('cm')

        self.assertEqual(p.value(), 100.0)
