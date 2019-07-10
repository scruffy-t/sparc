from unittest import TestCase
from sparc.core.node import AbstractNode
import copy


class TestAbstractNode(TestCase):

    def test_init(self):

        p1 = AbstractNode('param1')
        p2 = AbstractNode('param2')
        p1.add_child(p2)
        p3 = AbstractNode('üäö@€$?')
        p2.add_child(p3)
        p4 = AbstractNode('foo bar')
        p3.add_child(p4)
        p5 = AbstractNode('param2')
        p3.add_child(p5)

        self.assertEqual(p1.child_count(False), 1)
        self.assertEqual(p1.child_count(True), 4)
        self.assertEqual(p1['param2'], p2)
        self.assertEqual(p1['param2.üäö@€$?'], p3)
        self.assertEqual(p1['param2.üäö@€$?.foo_bar'], p4)
        self.assertEqual(p1['param2.üäö@€$?.param2'], p5)

        self.assertEqual(len(p3), 2)
        self.assertEqual(p3 in p2, True)
        self.assertEqual(p5 in p2, False)

        p1c = copy.copy(p1)
        self.assertEqual(p1c.parent(), None)
        self.assertEqual(p1c.child_count(True), 4)

        del p2[p3]
        self.assertEqual(p3 in p2, False)

        p1.remove_child(p2)
        self.assertEqual(p1.child_count(True), 0)
