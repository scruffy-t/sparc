from unittest import TestCase
from sparc.core import *


class TestTypes(TestCase):

    def test_init(self):

        class MyInt(object):
            def __init__(self, value):
                self.v = int(value)

            def __repr__(self):
                return repr(self.v)

            def __eq__(self, other):
                assert isinstance(other, MyInt)
                return self.v == other.v

        Types.register_type('MyInt', MyInt)

        p = ParamNode('test', value=34, type=MyInt)

        self.assertEqual(p.type(), MyInt)
        self.assertEqual(p.value(), MyInt(34))

        p.set_value(25)
        self.assertEqual(p.value(), MyInt(25))

        p = ParamNode('test', value='Hello', type=str)
        self.assertEqual(p.type(), str)
        self.assertEqual(p.value(), 'Hello')
