# param.py

# system modules
import re
import types
import collections

# sparc modules
from .node import AbstractNode, AbstractLeafNode
from .types import Types

__all__ = ['ParamGroupNode', 'ParamNode']


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
            parent_name, args[0] = AbstractNode.split_name(first)

            if parent_name != '':
                parent = self.child(parent_name)

            # if there is only one parameter given it must be a group node
            if len(args) + len(kwargs) == 1:
                node = ParamGroupNode(args[0])
            else:
                node = ParamNode(*args, **kwargs)

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
        children: Iterable
        """
        for child in children:
            if isinstance(child, (ParamNode, ParamGroupNode)):
                self.add_child(child)
            elif isinstance(child, collections.Mapping):
                self.add_child(**child)
            else:
                child_type = type(child)
                raise TypeError(f'unexpected type of child {child_type}')

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


def is_unbound(func):
    # builtin types
    if hasattr(func, '__objclass__'):
        return True
    # wrapped types
    elif hasattr(func, '__self__') and func.__self__ is None:
        return True
    # user pure Python types
    elif isinstance(func, types.FunctionType):
        return True
    return False


class ParamNode(AbstractLeafNode):

    VarPattern = r'([a-zA-Z_0-9]+(\.[a-zA-Z_0-9]+)*)(?![([a-zA-Z_0-9]])'

    def __init__(self, name=None, value=None, type=None, editable=True, validator=None, fget=None, fset=None, parent=None):
        """Constructs a new Param instance.
        Parameters
        ----------
        name: str or None
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
        if [name, fget].count(None) == 2:
            raise TypeError('at least one of name and fget must be provided')
        name = name or fget.__name__

        AbstractLeafNode.__init__(self, name, parent)

        # NOTE: don't infer type automatically, i.e. with self._t = type(value)
        # because we also support dynamic parameter types
        self._t = None

        # type parameter provided
        if isinstance(type, str):
            self._t = Types.get_type(type)
        elif type is not None:
            self._t = type

        self._validator = None
        # set validator before value to enable checking
        self.set_validator(validator)

        # TODO: how to handle fget/fset if classmethod, staticmethod, or builtin_method?

        if fget is not None:
            if not hasattr(fget, '__call__'):
                raise TypeError('fget must be None or a callable, not {}'.format(type(fget)))

            self._get = fget
        else:
            self._get = None  # will be set below in set_value

        if fset is not None:
            if not hasattr(fset, '__call__'):
                raise TypeError('fset must be None or a callable, not {}'.format(type(fset)))

        self._set = fset
        self._edit = True

        # if self.__is_expression(value):
        #     # type not allowed
        #     if type is not None:
        #         raise TypeError('type not allowed with expression')
        #     if validator is not None:
        #         raise TypeError('validator not allowed with expression')

        if value is not None and self.is_editable():
            self.set_value(value)  # convert, check, and set value

        self.set_editable(editable)  # set editable after value to enable value initialization

    def __call__(self, fget):
        self._get = fget
        # TODO: return a copy instead?
        return self

    def __get__(self, obj, owner):
        return self.value(obj=obj)

    def __set__(self, obj, value):
        return self.set_value(value, obj=obj)

    def is_descriptor(self):
        """Returns a bool indicating whether the node is a descriptor.
        Descriptors manage access to values that are hold by some other object.
        They do not hold their own values.
        """
        return isinstance(self._get, (types.MethodType, types.FunctionType))

    def is_editable(self):
        """Returns a bool indicating whether the underlying param node can be edited."""
        if self.is_descriptor():
            return self._edit and self._set is not None
        return self._edit

    def is_expression(self, *args, **kwargs):
        """Returns a bool indicating whether the param is an expression."""
        if self.is_descriptor():
            value = self._get(*args, **kwargs)
        else:
            value = self._get
        return self.__is_expression(value)

    def is_unbound(self):
        return is_unbound(self._get)

    def raw_value(self, obj=None):
        """Returns the node's raw value.
        Notes
        -----
        The raw_value of a node must not be equal to the value. E.g. in case
        of an expression node, the raw value is a str instance.
        """
        if self.is_descriptor():
            if self.is_unbound():
                return self._get(obj)
            else:
                return self._get()
        return self._get

    def setter(self, fset):
        self._set = fset
        # TODO: return a copy instead?
        return self

    def set_editable(self, editable):
        """
        """
        self._edit = editable

    def set_validator(self, validator):
        if validator is not None and not hasattr(validator, '__contains__'):
            raise AttributeError(f'validator {validator:!r} does not implement __contains__')
        self._validator = validator

    def set_value(self, value, obj=None):
        """Sets the node value.
        
        Parameters
        ----------
        value: any
        obj: Any
        
        Raises
        ------
        AttributeError:
            If node is not editable.
        ValueError:
            If value is not a valid value or expression.
        """
        if not self.is_editable():
            raise AttributeError(f'ParamNode {self.absolute_name()} is not editable')

        # check if value confirms to the value restrictions
        # imposed by type and validator
        # but only is value is not an expression
        # expressions are check whether they are valid only upon
        # access, i.e. when value() is called
        if not self.__is_expression(value):
            # may convert the value to the appropriate type
            # or raise an Error (ValueError or TypeError) if value
            # is not suitable
            value = self.__validate_value(value)

        if self.is_descriptor():
            if self.is_unbound():
                self._set(obj, value)
            else:
                self._set(value)

        else:
            self._get = value

    def type(self):
        """Returns the node value data type or None if type has not been set."""
        return self._t

    @staticmethod
    def expression_vars(expr):
        expr = expr.replace('= ', '')
        return [m.group() for m in re.finditer(ParamNode.VarPattern, expr)]

    def __validate_value(self, value):
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
        value_type = type(value)

        # type was set
        if self._t is not None:
            # deserialize string value only if node type is not str
            if isinstance(value, str) and self._t != str:
                try:
                    value = Types.deserialize(value, self._t)
                except SyntaxError:
                    raise ValueError(f'invalid value "{value}"')
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
            raise ValueError(f'validator rejected value {value}')

        return value

    def value(self, obj=None, context=None):
        """Returns the node value.
        Parameters
        ----------
        obj: object
        context: mapping
            The context provides values for external expression variables.
        """
        value = self.raw_value(obj)

        if self.__is_expression(value):
            value = self.__eval_expression(value, obj=obj, context=context)

        self.__validate_value(value)
        return value

    def validator(self):
        """Returns the node validator."""
        return self._validator

    def __eval_expression(self, expr, obj=None, context=None):
        """
        Parameters
        ----------
        expr: str
        context: Mapping or None
            Variable dict extension.
            NOTE: context values take precedence over sibling values!
        Raises
        ------
        NameError:
            If one of the variables is not a sibling node.
        """
        expr = expr.replace('= ', '')
        vars = [m.group() for m in re.finditer(self.VarPattern, expr)]

        if self.name() in vars:
            raise RecursionError('a node expression must not refer to the node itself')

        sibling_context = {}
        # overwrites kwargs with sibling node values
        for sibling in self.iter_siblings():
            if sibling.name() in vars:
                # TODO: check if sibling is a ParamGroupNode
                sibling_context[sibling.name()] = sibling.value(obj=obj, context=context)

        sibling_context.update(context or {})

        # for name in vars:
        #     context[name] = self.sibling(name).value(obj=obj, context=context)

        expr = expr.strip('= ')

        # TODO: replace eval with a safer way
        result = eval(expr, globals(), sibling_context)

        return result

    @staticmethod
    def __is_expression(value):
        """
        """
        return isinstance(value, str) and value.startswith('=')
