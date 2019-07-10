# types.py


class Types(object):

    TYPE_HINTS = {
        'int': int,
        'float': float,
        'list': list,
        'tuple': tuple,
        'bool': bool,
        'color': str,
        'str': str,
        'time': str,
        'date': str
    }

    @staticmethod
    def to_str(cls):
        for k, v in Types.TYPE_HINTS.items():
            if v == cls:
                return k
        raise KeyError('No conversion exists for type %s!' % str(cls))

    @staticmethod
    def register_type(key, cls):
        if not isinstance(cls, type):
            raise TypeError('Unexpected type of cls! cls must be a type')
        if key not in Types.TYPE_HINTS:
            Types.TYPE_HINTS[key] = cls
        else:
            raise KeyError(f'A type with key "{key}" is already registered!')

    @staticmethod
    def get_type(type_hint):
        if isinstance(type_hint, str):
            return Types.TYPE_HINTS[type_hint]
        if isinstance(type_hint, type):
            return type_hint
        raise TypeError('Unexpected type of type_hint!')

    @staticmethod
    def determine_type(value):
        return type(value)
