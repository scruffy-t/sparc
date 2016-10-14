import numbers
import re

from .abstract import AbstractParam
from .interval import Interval
from .types import Types

from pint import UnitRegistry
ureg = UnitRegistry()
Quant = ureg.Quantity

from math import *


class Param(AbstractParam):

    def __init__(self, name, value=0.0, type=None, values=Interval.inf(), unit='', parent=None):
        """
        Constructs a new Param with the given parameters.

        :param name: The parameter's name.
        :param value: The parameter's initial value.
        :param type: The type of the parameter value.
        :param values: Some object representing valid param values (must support __contains__ and __bool__).
                       Use 'None' or 'False' to make param non-editable or Interval or a list/tuple to limit
                       the param to a certain range or pre-defined choices.
        :param unit: A str representing the unit of the parameter.
        :param parent: The parameter's parent.
        :return:
        """
        AbstractParam.__init__(self, name, parent)

        if values is not None or values is not False:
            assert hasattr(values, '__contains__') and hasattr(values, '__bool__')

        self._t = type if type is not None else Types.determine_type(value)
        value = self._t(value)

        # store in a pint.Quantity object if value is a number and a unit was given
        if isinstance(value, numbers.Number) and unit != '':
            self._v = Quant(value, unit)
        else:
            self._v = value

        self._vs = values

    def convert_to(self, unit):
        """
        Converts the underlying param to the given unit if possible.

        :param unit:
        :return:
        """
        if self.is_quantity():
            self._v.ito(unit)
        else:
            raise AttributeError('Param instance is not a quantity')

    def is_editable(self):
        """
        Returns a bool indicating whether the underlying param instance can be edited.

        :return:
        """
        return bool(self._vs)

    def is_quantity(self):
        """
        Returns a bool indicating whether the underlying param instance is a physical quantity (has a unit).

        :return:
        """
        return isinstance(self._raw_data(), Quant)

    def is_valid(self):
        """
        Returns a bool indicating whether the underlying param instance is valid.

        A Param instance is considered valid if
        - it holds a valid value

        :return:
        """
        return self.is_valid_value(self.values())

    def is_valid_value(self, value):
        """
        Returns a bool indicating whether the given value is valid in respect to the underlying param instance.

        A value is considered valid if
        - it can be converted to the Param's value type
        - it is contained in the Param's values range

        :param value:
        :return:
        """
        try:
            value = self._t(value)
        except ValueError:
            return False
        return value in self._vs

    def set_unit(self, unit):
        """
        Set the unit of the underlying param instance.

        If the param didn't have a unit before, it will be converted to a pint.Quantity with a unit as specified.

        :param unit:
        """
        if self.is_quantity():
            self._v.units = unit
        else:
            self._v = Quant(self._v, unit)

    def set_value(self, value):
        if self.is_valid_value(value):
            value = self._t(value)
            if self.is_quantity():
                self._v = Quant(value, self.unit())
            else:
                self._v = value
        else:
            raise ValueError('Param %s is not editable or value %s is not valid' % (self._n, str(value)))

    def type(self):
        return self._t

    def unit(self):
        if self.is_quantity():
            return self._v.units
        return ''

    def value(self):
        if self.is_quantity():
            return self._v.magnitude
        return self._v

    def values(self):
        return self._vs

    def quantity(self):
        if self.is_quantity():
            return self._v
        return None

    #############################################
    # PROTECTED MEMBER METHODS
    #############################################

    def _raw_data(self):
        return self._v


class DependentParam(AbstractParam):

    VarPattern = r'([a-zA-Z_]+(\.[a-zA-Z_]+)*)(?![([a-zA-Z_]])'

    def __init__(self, name, expr, parent):
        AbstractParam.__init__(self, name, parent)
        self._varParams = []
        self.set_expr(expr)

    def expr(self):
        return self._v

    def is_quantity(self):
        return isinstance(self._raw_data(), Quant)

    def is_valid(self):
        """ Checks whether the given expression is valid, i.e. can be evaluated with pythons 'eval()'

        :return bool:
        """
        return self.is_valid_expr(self.expr())

    def is_valid_expr(self, expr):
        if expr == self.name():  # avoid getting trapped in infinite recursion
            return False

        try:
            self._eval_expr()
        except:
            return False

        return True

    def set_expr(self, expr):
        self._v = expr

        for param in self._varParams:
            param.name_changed.disconnect(self.update_variable_name)

        self._varParams = self._extract_expr_variables()

        for param in self._varParams:
            param.name_changed.connect(self.update_variable_name)

    def unit(self):
        if self.is_quantity():
            return self._eval_expr().units
        return ''

    def update_variable_name(self, old_name, new_name):
        self.set_expr(self.expr().replace(old_name, new_name))

    def value(self):
        result = self._eval_expr()
        if self.is_quantity():
            return result.magnitude
        return result

    def variables(self):
        return self._varParams

    def variable_names(self):
        return [param.name() for param in self.variables()]

    #############################################
    # PROTECTED MEMBER METHODS
    #############################################

    def _eval_expr(self):
        # TODO: Replace globals() with {'__builtins__': None} and add all relevent functions to locals
        return eval(self._v, globals(), self._raw_sibling_data(name_filter=self.variable_names()))

    def _extract_expr_variables(self):
        assert self.parent()
        expr = self.expr().replace(' ', '')
        params = []
        for m in re.finditer(self.VarPattern, expr):
            name = m.group()
            param = self.sibling(name)
            if param is None:
                raise LookupError('Param with name %s does not exist' % name)
            params.append(param)
        return params

    def _raw_data(self):
        return self._eval_expr()