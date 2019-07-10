from unittest import TestCase
from pickle import dumps, loads
from sparc.core import ParamGroupNode, Interval


class TestIO(TestCase):

    def test(self):

        p = ParamGroupNode('quiche_loraine')

        ingredients = p.add_child('ingredients')
        ingredients.add_child('servings', value=4, type=int, validator=Interval(0, 10))
        ingredients.add_child('milk', value='=0.1 * servings')

        loads(dumps(p))
