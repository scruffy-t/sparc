# --*-- encoding: utf-8 --*--

from unittest import TestCase
from sparc.core import AbstractParamNode


class TestAbstractParam(TestCase):

    def test_init(self):

        p1 = AbstractParamNode(u'param1')
        p2 = AbstractParamNode(u'param2', p1)
        p3 = AbstractParamNode(u'üäö@€$?')
        p4 = AbstractParamNode(u'foo bar')
        p5 = AbstractParamNode(u'param2')

        p2.add_child(p1)
        p3.add_child(p2)
        p3.add_child(p4)

        self.assertEqual(p2['param1'], p1)
        self.assertEqual(p3['param2.param1'], p1)
        self.assertEqual(len(p3), 2)
        self.assertEqual(p2 in p3, True)
        self.assertEqual(p5 in p3, False)

        del p3[p2]
        self.assertEqual(p2 in p3, False)

        p3.add_child(p5)
        self.assertEqual(p5 in p3, True)
