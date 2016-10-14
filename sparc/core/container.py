from .interval import Interval
from .abstract import AbstractParamNode
from .param import Param, DependentParam


class ParamSet(AbstractParamNode):

    def __init__(self, name, parent=None):
        AbstractParamNode.__init__(self, name, parent)

    def add_child(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """

        # get first argument
        if not len(args):
            args = [kwargs.pop('name')]
        else:
            args = list(args)
        first = args[0]

        if 'parent' in kwargs.keys():
            raise KeyError('Non valid keyword argument: parent')

        # create param instance to be added
        if isinstance(first, str):
            if len(args) + len(kwargs) == 1:
                param = ParamSet(*args, **kwargs)
            elif 'expr' in kwargs:
                kwargs['parent'] = self
                param = DependentParam(*args, **kwargs)
            else:
                param = Param(*args, **kwargs)
        elif isinstance(first, AbstractParamNode):
            param = first
        else:
            raise TypeError('Unexpected parameter type!')

        AbstractParamNode.add_child(self, param)

        return param

    def update_values(self, other):
        """

        :param other: dict containing name-value pairs to update
        :return:
        """
        for name, value in other.items():
            self.child(name).set_value(value)


class ParamGroup(AbstractParamNode):
    """
    A ParamGroup acts like a table with Params as columns and ParamSets as rows.
    """

    def __init__(self, name, parent=None):
        AbstractParamNode.__init__(self, name, parent)
        self._cd = []  # column data

    def __contains__(self, param):
        return param.parent() == self

    def __getitem__(self, index):
        if isinstance(index, int):    # row
            return self._c[index].copy()
        elif isinstance(index, str):  # column
            return [child[index].copy() for child in self._c]

    def add(self, name, init_value, type=float, values=Interval.inf(), unit=''):
        data = {'name': name, 'value': init_value, 'type': type, 'values': values, 'unit': unit}
        self._cd.append(data)
        for params in self._c:
            params.add_child(**data)

    def add_child(self, *args, **kwargs):
        if not len(args):
            args = [kwargs['name']]
        else:
            args = list(args)
        name = args[0]

        row = ParamSet(name, parent=self)
        for data in self._cd:
            row.add_child(**data)
        row.update_values(kwargs)
        self._c.append(row)

    def column_count(self):
        return len(self._cd)
