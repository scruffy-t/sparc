from unittest import TestCase
from sparc.core import *


class TestDependentParam(TestCase):

    def test_init(self):

        p = ParamSet('set')
        p.add_child('m', 5.0, unit='kg')
        p.add_child('a', 2.0, unit='m/s**2')
        p.add_child('A', 4.0, unit='m**2')
        p.add_child('F', expr='m*a')
        p.add_child('Sigma', expr='F/A')
        p.add_child('l', expr='A**0.5')

        self.assertEqual(p.child('F').value(), 10.0)
        self.assertEqual(p.child('Sigma').value(), 2.5)
        self.assertEqual(p.child('l').value(), 2.0)
