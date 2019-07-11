from .node import AbstractNode, AbstractLeafNode
from .types import Types

import re

__all__ = ['ParamGroupNode', 'ParamNode', 'param']

# TODO: add configurable display names, help text (for tooltips)


class ParamGroupNode(AbstractNode):

    def __init__(self, name, children=(), parent=None):
        """Initializes a new ParamGroupNode.

        Parameters
        ----------
        name: str
            A unique node name.
        children: tuple
            A list of child nodes. The parent of all child nodes
            will be reset to `self`.
        parent: AbstractNode
        """
        AbstractNode.__init__(self, name, children, parent)

    def add_child(self, *args, **kwargs):
        """Adds a new child to the node.
        """
        # get first argument
        if not len(args):
            args = [kwargs.pop('name')]
        else:
            args = list(args)
        first = args[0]

        if 'parent' in kwargs.keys():
            raise KeyError('Non valid keyword argument: parent')

        parent = self

        # create node instance to be added
        if isinstance(first, str):

            # find parent node
            parent_name, child_name = AbstractNode.split_name(first)
            if parent_name != '':
                parent = self.child(parent_name)

            # if there is only one parameter given it must be a group node
            if len(args) + len(kwargs) == 1:
                node = ParamGroupNode(child_name)
            else:
                args = args[1:]
                node = ParamNode(child_name, *args, **kwargs)

        # parameter is a node already
        elif isinstance(first, (ParamNode, ParamGroupNode)):
            node = first
        else:
            raise TypeError('unexpected parameter type {}'.format(type(first)))

        AbstractNode.add_child(parent, node)
        return node

    def add_children(self, children):
        """Adds a list of children to the node.

        Parameters
        ----------
        children: tuple of dicts
        """
        for child in children:
            self.add_child(**child)

    def iter_child_values(self, recursive=False):
        """Iterates through all child node values (recursively).

        Parameters
        ----------
        recursive: bool
            Controls whether to iterator through child nodes only on the first level or
            (recursively) through all lower levels.
        """
        for node in self.iter_children(recursive=recursive):
            yield node.value()

    def to_dict(self):
        """Returns a dict representation of the node and
        all its children.
        """
        d = {}
        for child in self.iter_children():
            if isinstance(child, ParamNode):
                d[child.name()] = child.value()
            else:  # isinstance(child, ParamGroupNode)
                d[child.name()] = child.to_dict()
        return d

    def update_values(self, other):
        """Updates child values based on a dict.

        Parameters
        ----------
        other: dict
            A dict with child names as keys and nodes values as values.
        """
        for name, value in other.items():
            self.child(name).set_value(value)


class ParamNode(AbstractLeafNode):

    VarPattern = r'([a-zA-Z_0-9]+(\.[a-zA-Z_0-9]+)*)(?![([a-zA-Z_0-9]])'

    def __init__(self, name, value=None, type=None, editable=True, validator=None, parent=None):
        """Constructs a new Param instance.

        Parameters
        ----------
        name: str
            The node name.
        value: Any
            The node's initial value.
        type: str or type
            The type of the node value or a type name (str) that is registered with the Types registry.
        editable: bool
            Specifies whether the node will be editable. As default, nodes are editable.
        validator: tuple, list, Interval, None, or custom validator
            - None to disable value checking
            - Collection (e.g. tuple, list, set, etc.) for enumerated values
            - Interval, e.g. for int, float, time values within a limited continuous range
            - custom validator, must implement __contains__ (checking is done via: "value in validator")
        parent: AbstractNode
            The parameter's parent node.
        """
        AbstractLeafNode.__init__(self, name, parent)

        self._raw = None  # the node's raw value, will be set below (set_value)
        self._fget = None
        self._fset = None
        self._edit = True
        self._vars = []  # stores variable names if node is an expression

        # if self.__is_expression(value):
        #     # type not allowed
        #     if type is not None:
        #         raise TypeError('type not allowed with expression')
        #     if validator is not None:
        #         raise TypeError('validator not allowed with expression')

        # type parameter was set explicitly
        if isinstance(type, str):
            self._t = Types.get_type(type)
        elif type is not None:
            self._t = type
        # NOTE: don't infer type automatically, i.e. with self._t = type(value)
        # because we also support dynamic parameter types
        else:
            self._t = None

        if validator is not None and not hasattr(validator, '__contains__'):
            raise AttributeError(f'validator {validator:!r} does not implement __contains__')

        self._validator = validator  # set validator before value to enable checking
        if hasattr(value, '__call__'):
            self._fget = value
        else:
            self.set_value(value)  # convert, check, and set value
        self.set_editable(editable)  # set editable after value to enable value initialization

    def __get__(self, obj, owner):
        if obj is None:
            return self
        if self.is_descriptor():
            return self._fget(obj)
        raise AttributeError('param node is not readable')

    def __set__(self, obj, value):
        if not self.is_editable():
            raise AttributeError('param node is not editable')
        # TODO: do all the checking that we normally do in set_value
        self._fset(obj, value)

    def is_descriptor(self):
        return self._fget is not None

    def is_editable(self):
        """Returns a bool indicating whether the underlying param node can be edited."""
        return self._edit

    def is_expression(self):
        """Returns a bool indicating whether the param is an expression."""
        return self.__is_expression(self._raw)

    @staticmethod
    def is_valid_expression(expr):
        # TODO: Implement is_valid_expression
        return True

    def is_valid_value(self, value):
        """

        Parameters
        ----------
        value:
        """
        try:
            self.validate_value(value)
        except ValueError:
            return False
        return True

    def raw_value(self):
        """Returns the node's raw value.

        Notes
        -----
        The raw_value of a node must not be equal to the value. E.g. in case
        of an expression node, the raw value is a str instance.
        """
        return self._raw

    def setter(self, fset):
        """Decorator function.

        :param fset:
        :return:
        """
        editable = fset is not None
        self.set_editable(editable)
        self._fset = fset
        return self

    def set_editable(self, editable):
        """
        """
        self._edit = editable

    def set_value(self, value):
        """Sets the node value.

        Parameters
        ----------
        value: any

        Raises
        ------
        AttributeError:
            If param is not editable.
        ValueError:
            If value is not a valid value or expression.
        """
        if not self.is_editable():
            raise AttributeError('Node %s is not editable!' % str(self))

        # may convert the value to the appropriate type
        self._raw = self.validate_value(value)

        # reset expression variables
        self._vars = []

        # extract variable names if value is an expression
        if self.__is_expression(value):
            expr = value.replace('= ', '')
            for m in re.finditer(self.VarPattern, expr):
                self._vars.append(m.group())

    def type(self):
        """Returns the node value data type or None if type has not been set."""
        return self._t

    def validate_value(self, value):
        """Returns the validated value or raises an exception if the value is not valid.

        Notes
        -----
        A value is considered valid if
        - it has the node's data type (if it was set explicitly)
        - it is contained in the Param's values range,
          i.e. "value in validator" returns True

        Raises
        ------
        ValueError:
        TypeError:
        """
        if self.__is_expression(value):
            if self.is_valid_expression(value):
                return value
            raise ValueError('invalid expression')

        value_type = type(value)

        # type was set
        if self._t is not None:
            # deserialize string value only if node type is not str
            if isinstance(value, str) and self._t != str:
                value = Types.deserialize(value, self._t)
            elif value_type != self._t:
                # try to use the type directly to convert value
                try:
                    value = self._t(value)
                except Exception:
                    raise TypeError(f'value {value} has invalid type {value_type}')

        # validator has not been set
        if self._validator is None:
            return value

        # check the validator
        if value not in self._validator:
            raise ValueError('invalid value')

        return value

    def value(self, **context):
        """Returns the node value, i.e. the display data."""
        if self.is_expression():
            return self.__eval_expression(**context)
        return self._raw

    def validator(self):
        """Returns the node validator."""
        return self._validator

    def __eval_expression(self, **context):
        """

        Parameters
        ----------
        context: dict
            Variable dict extension.
            NOTE: node values take precedence over context values!

        Raises
        ------
        NameError:
            If one of the variables is not a sibling node.
        """
        # common_keys = set(self._vars).intersection(context.keys())
        # if len(common_keys):
        #     raise KeyError('Invalid context keys: %s' % common_keys)

        for sibling in self.iter_siblings():
            if sibling.name() in self._vars:
                # TODO: check if sibling is a ParamGroupNode
                context[sibling.name()] = sibling.value()

        # for name in self._vars:
        #     context[name] = self.sibling(name).value()

        expr = self._raw.strip('= ')

        # TODO: Replace globals() with {'__builtins__': None} and add all relevant functions to context
        result = eval(expr, globals(), context)

        return result

    @staticmethod
    def __is_expression(value):
        """
        """
        return isinstance(value, str) and value.startswith('=')


class param(object):

    def __init__(self, name=None, type=None, validator=None, parent=None):
        self.name = name
        self.type = type
        self.validator = validator
        self.parent = parent

    def __call__(self, fget):
        name = self.name or fget.__name__
        return ParamNode(name, value=fget, type=self.type, editable=False,
                         validator=self.validator, parent=self.parent)
