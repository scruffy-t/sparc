from unittest import TestCase
import pickle

from sparc.core import ParamGroupNode, Interval, dumps, loads


def node():
    p = ParamGroupNode('quiche_loraine')
    ingredients = p.add_child('ingredients')
    ingredients.add_child('servings', value=4, type=int, validator=Interval(0, 10))
    ingredients.add_child('milk', value='=0.1 * servings')
    return p


class TestIO(TestCase):

    def test_pickle(self):
        pickle.loads(pickle.dumps(node()))

    def test_json(self):
        loads(dumps(node()))
