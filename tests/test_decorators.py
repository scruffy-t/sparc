import unittest

from sparc.gui import param, group
from sparc.core import Interval


class TestDecorators(unittest.TestCase):

    def test_decorators(self):

        class Foo(object):

            def __init__(self, v):
                self._v = v

            @param(type=int, validator=Interval(0, 100))
            def value(self):
                return self._v

            @value.setter
            def value(self, v):
                self._v = v

        class Bar(object):

            def __init__(self, foo, bar):
                self._v = bar
                self._f = Foo(foo)

            @param(type=int)
            def value(self):
                return self._v

            @group
            def group(self):
                return self._f

            def twice_value(self):
                return 2 * self._v

        f = Foo(34)
        b = Bar(56, 72)

        b2 = param(type=int, fget=b.twice_value)

        print(type(b.twice_value))
        print(type(Bar.twice_value))

        self.assertEqual(f.value, 34)
        self.assertEqual(b.value, 72)
        self.assertEqual(b2.value(), 144)
        self.assertEqual(b.group.value, 56)

        f.value = 45
        self.assertEqual(f.value, 45)

        b.group.value = 81
        self.assertEqual(b.group.value, 81)
