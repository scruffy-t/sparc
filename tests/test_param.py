from unittest import TestCase
from sparc.core import ParamNode, ParamGroupNode, Interval, param

import random


# class Param(object):
#
#     def __init__(self, name=None, value=None, type=None, validator=None, fget=None, fset=None):
#         print('inside __init__')
#         editable = fset is not None
#         self.p = ParamNode(name, value, type, editable=editable, validator=validator)
#         self.fget = fget
#         self.fset = fset
#
#     def __call__(self, fget):
#         print('inside __call__')
#         self.fget = fget
#         return self
#
#     def __get__(self, instance, owner):
#         print('inside __get__')
#         if instance is None:
#             return self
#         return self.fget(instance)
#
#     def __set__(self, instance, value):
#         print('inside __set__')
#         if self.fset is None:
#             raise AttributeError('parameter {} is not editable'.format(self.p.name()))
#         return self.fset(instance, value)
#
#     def setter(self, fset):
#         print('inside setter')
#         return type(self)(name=self.p.name(), value=self.p.value(), type=self.p.type(), fget=self.fget, fset=fset)


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
        self.assertEqual(p.child('extern').value(x=2, F=34), 42.0)

        with self.assertRaises(NameError):
            p.child('extern').value()

    def test_property_wrapper(self):

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

            def __init__(self, v):
                self._v = v

            @param(type=float)
            def child_value(self):
                return self._v

        f1 = Foo(34)
        f2 = Foo(23)
        b1 = Bar(34.56)

        self.assertEqual(f1.value, 34)

        f1.value = 45

        self.assertEqual(f1.value, 45)
        self.assertEqual(f2.value, 23)

        p = ParamGroupNode('test')
        p.add_child(Foo.value)
