from unittest import TestCase
from sparc.core import Param, ParamSet, Interval

import json


class TestIO(TestCase):

    def test_json(self):
        p = ParamSet('set')
        p.add_child('x')
        p.add_child('y')
        p.add_child('z', expr='x+y')

        print(json.dumps(p, indent=4))
