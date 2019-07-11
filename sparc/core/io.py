# io.py

import json

from .param import ParamNode, ParamGroupNode
from .types import Types

__all__ = ['dumps', 'dump', 'loads', 'load']


class ParamNodeEncoder(json.JSONEncoder):

    def default(self, obj):

        if isinstance(obj, ParamNode):

            if obj.is_expression():
                value = obj.raw_value()
            else:
                val_type = obj.type()
                value = Types.serialize(val_type, obj.value())

            if obj.type() is not None:
                type_str = Types.get_name(obj.type())
            else:
                type_str = None

            if obj.validator() is not None:
                val_type = type(obj.validator())
                validator = Types.serialize(val_type, obj.validator())
            else:
                validator = None

            return {
                'name': obj.absolute_name(),
                'value': value,
                'type': type_str,
                'editable': obj.is_editable(),
                'validator': validator
            }

        elif isinstance(obj, ParamGroupNode):

            return {
                'name': obj.absolute_name()
            }

        return super(ParamNodeEncoder, self).default(obj)


class ParamNodeDecoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
        self._nodes = {}

    def object_hook(self, obj):

        if 'name' in obj and 'value' in obj:

            parent, name = ParamGroupNode.split_name(obj['name'])
            obj['name'] = name

            if obj['type'] is not None:
                type_cls = Types.get_type(obj['type'])
                obj['type'] = Types.deserialize(obj['type'], type_cls)

            if obj['validator'] is not None:
                obj['validator'] = Types.deserialize(obj['validator'])

            if parent != '':
                parent_node = self._nodes[parent]
                obj = parent_node.add_child(**obj)
            else:
                obj = ParamNode(**obj)

            self._nodes[obj.absolute_name()] = obj

        elif 'name' in obj:

            parent, name = ParamGroupNode.split_name(obj['name'])
            obj['name'] = name

            if parent != '':
                try:
                    parent_node = self._nodes[parent]
                except KeyError:
                    raise IOError(f'parent node {parent} of node {name} does not exist')

                obj = parent_node.add_child(**obj)
            else:
                obj = ParamGroupNode(**obj)

            self._nodes[obj.absolute_name()] = obj

        return obj


def dumps(node, indent=None):
    nodes = [node] + [n for n in node.iter_children(recursive=True)]
    return json.dumps(nodes, cls=ParamNodeEncoder, indent=indent)


def dump(node, fp, indent=None):
    nodes = [node] + [n for n in node.iter_children(recursive=True)]
    json.dump(nodes, fp, cls=ParamNodeEncoder, indent=indent)


def loads(s):
    """

    Parameters
    ----------
    s: str, bytes, or bytearray
    """
    nodes = json.loads(s, cls=ParamNodeDecoder)
    return nodes[0]


def load(fp):
    nodes = json.load(fp, cls=ParamNodeDecoder)
    return nodes[0]
