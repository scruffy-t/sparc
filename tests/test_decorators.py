import unittest

from sparc.core import Interval, ParamNode, ParamGroupNode


class TestDecorators(unittest.TestCase):

    def test_class_decorators(self):

        class Foo(object):

            def __init__(self, v):
                self._v = v

            @ParamNode('value', type=int, validator=Interval(0, 100))
            def value(self):
                return self._v

            @value.setter
            def value(self, v):
                self._v = v

        a = Foo(34)
        self.assertEqual(a.value, 34)

        a.value = 50
        self.assertEqual(a.value, 50)

        with self.assertRaises(ValueError):
            a.value = 101

    def test_bound_descriptor(self):

        class Bar(object):

            def __init__(self, v):
                self._v = v

            def value(self):
                return self._v

            def set_value(self, v):
                self._v = v

        b = Bar(3)
        p = ParamNode(type=int, validator=Interval(0, 5), fget=b.value, fset=b.set_value)

        self.assertEqual(p.name(), b.value.__name__)
        self.assertEqual(b.value(), p.value())

        b.set_value(4)
        self.assertEqual(b.value(), p.value())

        p.set_value(5)
        self.assertEqual(b.value(), p.value())

        with self.assertRaises(ValueError):
            p.set_value(6)

        # unfortunately, it is still possible to assign
        # an invalid value to the data object directly
        b.set_value(6)

        # but a ValueError will be thrown when we try
        # to access the value
        with self.assertRaises(ValueError):
            p.value()

    def test_unbound_descriptor(self):

        factor = 4

        class Bar(object):

            def __init__(self, v):
                self._v = v

            def expression(self):
                return f'= {factor} * value'

            def value(self):
                return self._v

            def set_value(self, v):
                self._v = v

        b = Bar(3)

        p1 = ParamNode(type=int, validator=Interval(0, 5), fget=Bar.value, fset=Bar.set_value)

        self.assertEqual(p1.name(), Bar.value.__name__)
        self.assertEqual(b.value(), p1.value(obj=b))

        b.set_value(4)
        self.assertEqual(b.value(), p1.value(obj=b))

        p1.set_value(5, obj=b)
        self.assertEqual(b.value(), p1.value(obj=b))

        with self.assertRaises(ValueError):
            p1.set_value(6, obj=b)

        # unfortunately, it is still possible to assign
        # an invalid value to the data object directly
        b.set_value(6)

        # but a ValueError will be thrown when we try
        # to access the invalid value
        with self.assertRaises(ValueError):
            p1.value(obj=b)

        # replace invalid value set above
        b.set_value(5)

        p2 = ParamNode(type=int, fget=Bar.expression)
        self.assertTrue(p2.is_unbound())

        group = ParamGroupNode('group')
        group.add_children([p1, p2])

        self.assertEqual(p2.value(obj=b), factor * p1.value(obj=b))
