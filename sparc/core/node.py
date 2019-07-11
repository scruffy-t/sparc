# node.py
"""Basic node classes.

This module defines two classes that implement basic tree node
functionality.

Classes:
    AbstractLeafNode: A class that implements basic tree node functionality
    for leaf node, i.e. nodes without children.

    AbstractNode: A class that implements basic tree node functionality for
    adding, accessing, and removing child nodes.
"""
LEVEL_SEPARATOR = '.'


class AbstractLeafNode(object):
    """Base class of all node classes.

    The AbstractLeafNode class provides basic tree node functionality
    but provides *no* members for handling children or data at the node
    level.

    See ``AbstractNode`` for a subclass that can also handle child nodes.

    See ``ParamNode`` or one of its subclasses if you need nodes that
    can hold arbitrary data.
    """

    def __init__(self, name, parent=None):
        """Initializes a new AbstractLeafNode.

        Parameters
        ----------
        name: str
            A unique node name. Whitespaces will be replaced by "_"
            and the ``LEVEL_SEPARATOR`` str is not allowed. The name
            is used to identify a node in a node tree. Therefore, it
            must be unique on a tree level.
        parent: AbstractNode or None
            Parent node.
        """
        # the node name is used to identify a node in a node tree.
        # therefore it must be unique on a tree level and must not
        # contain the LEVEL_SEPARATOR string.
        self._n = self.validate_name(name)
        self._p = None  # the parent node

        if parent is not None:
            if self._n in parent.child_names():
                raise NameError('Node {} already has a child with name {}'.format(parent.name(), self._n))
            parent.add_child(self)  # sets self._p = parent

    def index(self):
        """Returns the index of the node if it has a parent, otherwise None."""
        if self.parent() is None:
            return None
        return self.parent().index_of_child(self.name())

    def sibling(self, node):
        """Returns a sibling node.

        Parameters
        ----------
        node: int or str
            The name or index of sibling node.
        """
        if not self.has_siblings():
            raise ValueError('Node has no siblings')
        return self.parent().child(node)  # may raise ValueError if child does not exist

    def sibling_count(self):
        """Returns the number of siblings."""
        if not self.has_siblings():
            return 0
        return self.parent().child_count() - 1

    def has_siblings(self):
        """Returns a bool indicating whether the node has siblings."""
        if self.parent() is None:
            return False
        return len(self.parent()) > 1

    def has_children(self):
        return False

    def iter_siblings(self):
        """Iterates over all siblings."""
        if self.parent() is None:
            raise StopIteration
        for sibling in self.parent().iter_children():
            if sibling is not self:
                yield sibling

    def parent(self):
        """Returns the node's parent."""
        return self._p

    def root(self):
        """Returns the root node of the node tree or ``self`` if the node has no parent."""
        root = self
        while root.parent() is not None:
            root = root.parent()
        return root

    def name(self):
        """Returns the node name."""
        return self._n

    def display_name(self):
        """Returns the display name of the node.

        Underscore characters are replaced by whitespaces.

        Examples
        --------

        >>> n = AbstractLeafNode('node_name')
        >>> n.display_name()
        'node name'
        """
        return self._n.replace('_', ' ')

    def absolute_name(self):
        """Returns the absolute name of the node, similar to an absolute path.

        Levels are separated by the LEVEL_SEPARATOR.

        Examples
        --------

        >>> parent = AbstractNode('parent')
        >>> child = AbstractLeafNode('child')
        >>> parent.add_child(child)
        >>> child.absolute_name()
        'parent.child'
        """
        root = self.root()
        if root is not self:
            return root.name() + LEVEL_SEPARATOR + self.relative_name(root)
        return self.name()

    def relative_name(self, node):
        """Returns the node name relative to *node*.

        Parameters
        ----------
        node: AbstractNode
            Must be a higher level parent node of the calling node.
        """
        parent = self.parent()
        path = [self, ]
        found = False

        while parent:
            if parent == node:
                found = True
                break
            path.append(parent)
            parent = parent.parent()

        if found:
            return LEVEL_SEPARATOR.join(map(lambda n: n.name(), reversed(path)))

        raise ValueError('node %s is not a parent of %s' % (node.name(), self.name()))

    def set_parent(self, parent):
        """(Re)sets the node's parent.

        Removes ``self`` from a possibly pre-existing parent, but
        does not add ``self`` to parent. Use parent.add_child() for that.

        Parameters
        ----------
        parent: AbstractNode
        """
        old_parent = self.parent()
        if parent == old_parent:
            return

        if old_parent is not None:
            old_parent.remove_child(self)

        self._p = parent

    @staticmethod
    def node_name(node_or_str):
        """Utility function that returns a str object representing a node name.

        Parameters
        ----------
        node_or_str: AbstractLeafNode or str
        """
        if type(node_or_str) == str:
            return node_or_str
        elif isinstance(node_or_str, AbstractLeafNode):
            return node_or_str.name()

        raise TypeError('Unexpected type of argument: %s. Supported types: str, AbstractLeafNode' % type(node_or_str))

    @staticmethod
    def validate_name(node):
        """Returns the validated node name or raises a ValueError if the name is not valid.
        """
        name = AbstractLeafNode.node_name(node)
        name = name.replace(' ', '_')

        if LEVEL_SEPARATOR in name:
            raise ValueError('node names may not contain the level separator "%s"!' % LEVEL_SEPARATOR)

        return name


class AbstractNode(AbstractLeafNode):
    """Base class of node classes that can have child nodes.

    Implements the basic functionality of a tree node, e.g.
    - adding new child nodes
    - accessing child nodes
    - iterating over child nodes

    The AbstractNode class provides *no* members for handling data at the node
    level. See `ParamNode` or a subclass that
    can hold arbitrary data.
    """

    def __init__(self, name, children=(), parent=None):
        """Constructor.

        Parameters
        ----------
        name: str
        children: tuple
            A list of child nodes.
        """
        AbstractLeafNode.__init__(self, name, parent)
        if parent is not None:
            if not isinstance(parent, AbstractNode):
                raise TypeError()

        self._c = []
        for child in children:
            self.add_child(child)

    def __contains__(self, node):
        """Tests whether node is a child of ``self``."""
        return node in self._c

    def __iter__(self):
        """First level (non-recursive) iteration through all children of ``self``."""
        return self.iter_children()

    def __len__(self):
        """Returns the number of first level child nodes."""
        return self.child_count()

    def __getitem__(self, index):
        """Returns the child node at the given index.

        Parameters
        ----------
        index: int or str
            The child's list index or name.
        """
        return self.child(index)

    def __delitem__(self, node):
        self.delete_child(node)

    def add_child(self, node):
        """Adds the given node as a child.

        Checks whether a node with same name already exists and the
        given node name is valid.

        Parameters
        ----------
        node: AbstractLeafNode, AbstractNode or str
            If node is an AbstractLeafNode or AbstractNode, its parent will be
            reset to self. If node is a str, a new AbstractNode will be created.
        """
        if isinstance(node, str):
            node = AbstractNode(node, parent=self)

        if not isinstance(node, AbstractLeafNode):
            raise TypeError('node must be a str or AbstractLeafNode instance')

        if node.name() in self.child_names():
            raise KeyError('A node with name "%s" already exists!' % node.name())

        node.set_parent(self)

        # add param to child list
        self._c.append(node)

        return node

    def child(self, index):
        """Returns the child with given name or index.

        Parameters
        ----------
        index: int or str
            the child's list index or name.

        Raises
        ------
        TypeError:
            If `index` is not an int or str.
        ValueError:
            If `index` does not specify a valid child.

        When the child name (a str instance) is provided, several child levels can be searched by
        using the LEVEL_SEPARATOR. For example (with LEVEL_SEPARATOR = '.')

        >>> root = AbstractNode('my_params', parent=None)
        >>> p1 = AbstractNode('child')
        >>> root.add_child(p1)
        >>> p2 = AbstractNode('grand_child')
        >>> p1.add_child(p2)
        >>> root.child('child.grand_child') == p2
        >>> root.child('child').child('grand_child') == p2
        >>> # it is also possible to use Python's built-in __getitem__
        >>> # member to access child nodes. To access p2 from the
        >>> # previous example you could also write:
        >>> root['child.grand_child'] == p2
        >>> # or, using integer indexing:
        >>> root[0][0] == p2

        Notes
        -----
        If performance is important, and you maintain large node trees, you should always prefer integer
        indexing to access child nodes as this is the fastest way of retrieving child nodes.
        """
        if type(index) is int:
            return self._c[index]

        if type(index) is not str:
            raise TypeError('Unexpected index type %s. Supported types are: int, str' % type(index))

        # index is str instance
        if LEVEL_SEPARATOR in index:
            child = None
            parent = self
            for name in index.split(LEVEL_SEPARATOR):
                child = parent.child(name)  # may raise ValueError
                parent = child
            return child

        # else, i.e. index does not contain LEVEL_SEPARATOR
        return self._c[self.index_of_child(index)]  # may raise ValueError

    def child_count(self, recursive=False):
        """Returns the number of child nodes.

        Parameters
        ----------
        recursive: bool
            Whether to count also level-2+ child nodes.
        """
        if not recursive:
            return len(self._c)
        return sum([1 for _ in self.iter_children(recursive)])

    def index_of_child(self, node):
        """Returns the index of a first level child node.

        Parameters
        ----------
        node: AbstractLeafNode or str
            node or name of node of which the index is requested.
            Otherwise a TypeError is raised.

        Raises
        ------
        TypeError:
            If `node` is not an AbstractLeafNode or str.
        ValueError:
            If `node` is not a child.
        """
        if isinstance(node, AbstractLeafNode):
            return self._c.index(node)  # may raise ValueError

        name = self.node_name(node)  # may raise TypeError
        return self.child_names().index(name)  # may raise ValueError

    def remove_child(self, node):
        """Removes the specified first level child node.

        Parameters
        ----------
        node: AbstractLeafNode, str, or int
            node must be a first level child.
        """
        if isinstance(node, AbstractLeafNode):
            self._c.remove(node)
        else:  # node is int or str
            self.remove_child(self.child(node))  # let remove_child raise an error if necessary

    def pop_child(self, node):
        """Pops the specified first level child node.

        Parameters
        ----------
        node: AbstractLeafNode or str

        Raises
        ------
        ValueError: raises ValueError if param is not a child
        """
        node = self._c.pop(self.index_of_child(node))
        return node

    def delete_child(self, node):
        """Deletes the specified first level child node.

        Parameters
        ----------
        node: AbstractLeafNode or str

        Raises
        ------
        ValueError: raises ValueError if param is not a child
        """
        node = self.pop_child(node)
        del node

    def child_names(self, recursive=False):
        """Returns a list of all child names.

        Parameters
        ----------
        recursive: bool
            If set to True, all child levels will be collected recursively and
            node names will be relative to caller instance.
        """
        return [param.relative_name(self) for param in self.iter_children(recursive=recursive)]

    def has_children(self):
        """Returns a bool indicating whether the node has children."""
        return bool(len(self._c))

    def iter_children(self, recursive=False):
        """Iterates all child nodes.

        The non-recursive version of iterating child nodes can also be accessed via the
        __iter__ member, e.g.

        Examples
        --------

        >>> parent = AbstractNode('parent')
        >>> child = parent.add_child('child')
        >>> grand_child = child.add_child('grand child')
        ...
        >>> # non-recursive iteration
        >>> for child in parent:
        >>>     print(child.name())
        ...
        >>> # recursive iteration
        >>> for child in parent.iter_children(recursive=True):
        >>>     print(child.name())
        """
        for child in self._c:
            yield child
            if recursive and child.has_children():
                for grand_child in child.iter_children(recursive=recursive):
                    yield grand_child

    @staticmethod
    def split_name(name):
        """

        Parameters
        ----------
        name: str
        """
        index = name.rfind(LEVEL_SEPARATOR)
        if index == -1:
            return '', name
        return name[:index], name[index+1:]
