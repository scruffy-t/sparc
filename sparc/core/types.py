# types.py

# system modules
from datetime import time, date, datetime

# sparc modules
from .interval import Interval

__all__ = ['Types']


TYPE_NAMES = {
    'int': int,
    'float': float,
    'list': list,
    'tuple': tuple,
    'bool': bool,
    'str': str,
    'time': time,
    'date': date,
    'datetime': datetime,
    'Interval': Interval
}

TYPE_SERIALIZER = {}


class ReprSerializer(object):

    @staticmethod
    def deserialize(text, **subs):
        glob = globals().copy()
        glob.update(**subs)
        return eval(text, glob)

    @staticmethod
    def serialize(obj):
        return repr(obj)


class Types(object):

    @staticmethod
    def deserialize(text, cls=None):
        if cls is None:
            serializer = ReprSerializer
        else:
            serializer = Types.get_serializer(cls)
        return serializer.deserialize(text, **TYPE_NAMES)

    @staticmethod
    def determine_type(obj):
        return type(obj)

    @staticmethod
    def get_name(cls):
        for k, v in TYPE_NAMES.items():
            if v == cls:
                return k
        raise KeyError(f'no conversion exists for type {cls:!r}')

    @staticmethod
    def get_type(name):
        if isinstance(name, str):
            return TYPE_NAMES[name]
        raise TypeError('unexpected type of "name": {}'.format(type(name)))

    @staticmethod
    def get_serializer(cls):
        """

        Parameters
        ----------
        cls: str or type
        """
        if isinstance(cls, str):
            cls = Types.get_type(cls)
        if isinstance(cls, type):
            return TYPE_SERIALIZER.get(cls, ReprSerializer)
        raise TypeError('unexpected type of "cls"')

    @staticmethod
    def register_type(name, cls, serializer=None):
        if not isinstance(cls, type):
            raise TypeError('unexpected type of cls! cls must be a type')
        if name not in TYPE_NAMES:
            TYPE_NAMES[name] = cls
            if serializer is not None:
                TYPE_SERIALIZER[cls] = serializer
        else:
            raise KeyError(f'a type with key "{name}" is already registered')

    @staticmethod
    def serialize(cls, obj):
        serializer = Types.get_serializer(cls)
        return serializer.serialize(obj)
