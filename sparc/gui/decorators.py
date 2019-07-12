__all__ = ['group', 'param']


class group(property):

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        super(group, self).__init__(fget, fset, fdel, doc)


class param(object):

    def __init__(self, type=None, validator=None, fget=None, fset=None, fdel=None):
        self._t = type
        self._v = validator
        self.fget = fget
        self.fset = fset
        self.fdel = fdel

    def __call__(self, fget):
        return self.getter(fget)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError('param is not deletable')
        return self.fdel(obj)

    def __get__(self, obj, owner):
        if self.fget is None:
            raise AttributeError('param is not readable')
        if obj is None:
            return self
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError('param is not editable')
        # TODO: do type and validator checking
        return self.fset(obj, value)

    def deleter(self, fdel):
        return type(self)(self._t, self._v, self.fget, self.fset, fdel)

    def getter(self, fget):
        return type(self)(self._t, self._v, fget, self.fset, self.fdel)

    def is_editable(self):
        return self.fset is not None

    def setter(self, fset):
        return type(self)(self._t, self._v, self.fget, fset, self.fdel)

    def type(self):
        return self._t

    def validator(self):
        return self._v

    def value(self, obj):
        return self.__get__(obj, None)

