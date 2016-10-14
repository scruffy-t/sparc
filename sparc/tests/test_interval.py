# --*-- encoding: utf-8 --*--

from unittest import TestCase
from sparc.core import Interval


class TestInterval(TestCase):

    def test_init(self):

        int1 = Interval('(-1.45, 2]')
        self.assertEqual(int1.min, -1.45)
        self.assertEqual(int1.max, 2)
        self.assertEqual(0.5 in int1, True)
        self.assertEqual(0 in int1, True)

        int2 = eval(repr(int1))
        self.assertEqual(int1.min, int2.min)
        self.assertEqual(int1.max, int2.max)
        self.assertEqual(int1.min_bound, int2.min_bound)
        self.assertEqual(int1.max_bound, int2.max_bound)
