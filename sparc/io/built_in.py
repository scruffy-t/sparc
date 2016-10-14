from sparc.core import *

import json


class ParamEncoder(json.JSONEncoder):
    def default(self, obj):
        # TODO: Implement custom JSON encoder
        if isinstance(obj, ParamSet):
            return []
        elif isinstance(obj, ParamGroup):
            return []
        elif isinstance(obj, Param):
            return []
        elif isinstance(obj, DependentParam):
            return []
        elif isinstance(obj, Interval):
            return []
        # let the base class default method raise a TypeError
        return json.JSONEncoder.default(self, obj)
