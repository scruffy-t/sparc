from unittest import TestCase
from sparc.core import Param, ParamSet, Interval

import random
import string


class TestParamSet(TestCase):

    def test_add(self):
        p = ParamSet('test')
        p.add_child('x', 1, int, Interval(0, 1))
        p.add_child('y', 1, values=Interval(0, 1))
        p.add_child(Param('z', value=1, type=int, values=Interval(0, 1)))

        self.assertEqual(p['x'].value(), 1)
        self.assertEqual(p['y'].value(), 1)
        self.assertEqual(p['z'].value(), 1)

    def test_contains(self):
        p = ParamSet('test')

        c1 = Param('x', p)
        c2 = Param('y', p)

        p.add_child(c1)

        self.assertEqual(c1 in p, True)
        self.assertEqual(c2 in p, False)

    def test_iter(self):
        p = ParamSet('test')

        for i in range(10):
            name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
            p.add_child(Param(name))

        last_name = '00000'
        for param in p:
            self.assertNotEqual(param.name(), last_name)
            last_name = param.name()

        some_child = p.child(0)
        for sibling in some_child.iter_siblings():
            self.assertTrue(some_child is not sibling)
            self.assertEqual(some_child.parent(), sibling.parent())

    def test_grandChildParam(self):
        p = ParamSet('grandParent')
        pp = ParamSet('parent')
        ppp = Param('child', random.randint(0, 100))
        pppp = Param('grandChild')

        p.add_child(pp)
        pp.add_child(ppp)
        ppp.add_child(pppp)

        self.assertEqual(p['parent.child'].value(), ppp.value())
        self.assertEqual(ppp.relative_name(p), 'parent.child')
        self.assertEqual(pppp.absolute_name(), 'grandParent.parent.child.grandChild')

    def test_update(self):
        p = ParamSet('set')
        p.add_child('x', values=Interval(-1, 1))
        p.add_child('y', values=Interval(-1, 1))
        p.add_child('z', values=Interval(-1, 1))

        p.add_child('a').add_child('b', values=Interval(-1, 1))

        u = {'x': 0.0, 'y': 1.0, 'z': 0.5, 'a.b': 0.2}
        p.update_values(u)

        self.assertEqual(p['x'].value(), u['x'])
        self.assertEqual(p['y'].value(), u['y'])
        self.assertEqual(p['z'].value(), u['z'])

        self.assertEqual(p['a.b'].value(), u['a.b'])
        self.assertEqual(p.child('a')['b'].value(), u['a.b'])
