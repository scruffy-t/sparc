from .signals import Signal


class AbstractParamNode(object):
    """ Base class of most **sparc** classes.

    Implements the basic functionality of a tree node, e.g.
    - adding new child nodes
    - accessing child nodes
    - iterating over child and sibling nodes

    The AbstractParamNode class provides *no* members for handling data at the node
    level. See ``AbstractParam`` or one of its subclasses if you need nodes that
    can hold (arbitrary) data objects.

    :ivar _n: unique node name (whitespace characters will be replaced by "_" characters)
    :ivar _p: parent node (can be None or another AbstractParamNode instance)
    :ivar _c: the list of child nodes
    """

    def __init__(self, name, parent=None):
        """

        :param name:
        :param parent:
        :return:
        """
        assert isinstance(parent, AbstractParamNode) or parent is None

        self._p = parent
        self._n = self.__validate_child_name(name, parent)
        self._c = []

        self.name_changed = Signal()    # __call__(old_name, new_name)
        self.child_added = Signal()     # __call__(new_child)
        self.child_removed = Signal()   # __call__()
        self.parent_changed = Signal()  # __call__(old_parent, new_parent)

    def __contains__(self, param):
        return param in self._c

    def __iter__(self):
        return self.iter_children()

    def __len__(self):
        return len(self._c)

    def __getitem__(self, name):
        return self.child(name)

    def __delitem__(self, param):
        self.remove_child(param)

    def index(self):
        """
        :return: index of underlying param node instance or None if node has no parent node
        """
        if not self.parent():
            return None
        return self.parent().index_of_child(self.name())

    # --- COPY / CLONE ---

    def clone(self, parent, recursive=False):
        pass

    def copy(self, parent, recursive=False):
        pass

    # --- CHILDREN ---

    def add_child(self, node):
        """ Add new child param.

        Checks whether a param with same name already exists, the
        given param name is valid (does not contain '.' characters),
        and adds the given param to the child list.

        :param node: an instance of AbstractParamNode to be added to the child list
        """
        assert isinstance(node, AbstractParamNode)

        # check if param with same name already exists
        self.__validate_child_name(node)
        # add param to child list
        self._c.append(node)

        # reset params parent to self
        # NOTE: automatically removes param from the child list of an already existing parent
        node.__reset_parent(self)

        self.child_added(node)

    def child(self, index):
        """ Returns the child with given name or index.

        When the child name (a str instance) is provided, several child levels can be searched by
        using '.' notation. For example

        >>> from sparc.core import AbstractParamNode
        >>> params = AbstractParamNode('my_params', parent=None)
        >>> p1 = AbstractParamNode('child')
        >>> params.add_child(p1)
        >>> p2 = AbstractParamNode('grand_child')
        >>> p1.add_child(p2)
        >>> params.child('child.grand_child') == p2
        ... # doctest: +NORMALIZE_WHITESPACE
        >>> params.child('child').child('grand_child') == p2
        ... # doctest: +NORMALIZE_WHITESPACE
        >>> # it is also possible to use Python's built-in __getitem__
        >>> # member to access child nodes. To access p2 from the
        >>> # previous example you could also write:
        >>> param['child.grand_child'] == p2
        ... # doctest: +NORMALIZE_WHITESPACE
        >>> # or, using integer indexing:
        >>> param[0][0] == p2
        ... # doctest: +NORMALIZE_WHITESPACE

        NOTE: If performance is important to you, and you maintain large param trees, you should always prefer integer
        indexing to access child nodes as it is considerably faster.

        :param index: int or str, representing the child's list index and name, respectively
        :return: child node that was requested
        """

        if type(index) is int:
            return self._c[index]
        if type(index) is not str:
            raise TypeError('Unexpected index type %s. Supported types are: int, str' % type(index))

        if '.' in index:
            child = None
            parent = self
            for name in index.split('.'):
                child = parent.child(name)
                parent = child
            return child

        # else (index does not contain '.')
        return self._c[self.index_of_child(index)]

    def index_of_child(self, node):
        """ Returns index of child param or raises ValueError if child does not exist.

        :param node: param or name of param of which the index is requested
        :return: list index of param

        :raises ValueError: raises ValueError if param is not a child
        """
        name = self.node_name(node)
        return self.child_names().index(name)

    def remove_child(self, node):
        """
        Removes the specified child node from the child list

        :param node: node or name of node to be removed

        :raises ValueError: raises ValueError if param is not a child
        """
        del self._c[self.index_of_child(node)]
        self.child_removed()

    def child_names(self, recursive=False):
        """
        Return a list of all child names.

        :param recursive: if set to True, all child levels will be collected recursively
        :return: a list of param names. If recursive is True, names will be relative to caller instance
        """
        return [param.relative_name(self) for param in self.iter_children(recursive=recursive)]

    def has_children(self):
        return bool(len(self._c))

    def iter_children(self, recursive=False):
        for child in self._c:
            yield child
            if recursive and child.has_children():
                for grand_child in child.iter_children(recursive=recursive):
                    yield grand_child

    # --- SIBLINGS ---

    def sibling(self, name):
        """
        Return sibling node with given name

        :param name: name (str) of sibling node
        :return: sibling node that was requested
        """
        assert type(name) == str
        if not self.parent():
            return None
        return self.parent().child(name)

    def has_siblings(self):
        if self.parent() is None:
            return False
        return len(self.parent()) > 1

    def iter_siblings(self):
        if not self.parent():
            raise StopIteration
        for sibling in self.parent().iter_children():
            if sibling is not self:
                yield sibling

    # --- PARENT ---

    def parent(self):
        """
        Returns the node's parent.

        :return: parent param node or None if node has no parent
        """
        return self._p

    def root(self):
        """
        Returns the root node of the whole node tree.

        :return: top most node of the whole node tree or self if node has no parent.
        """
        root = self
        while root is not None:
            if root.parent() is None:
                break
            root = root.parent()
        return root

    # --- NAME ----

    def name(self):
        """
        Returns param node name.

        :return: a str representing the name of the param node
        """
        return self._n

    def set_name(self, name):
        """
        Sets the name of the node.

        :param name: str representing the new param name.
        """
        if name == self.name():
            return

        old_name = self._n
        self._n = self.__validate_child_name(name)
        self.name_changed(old_name, self._n)

    def display_name(self):
        return self._n.replace('_', ' ')

    def absolute_name(self):
        root = self.root()
        if root is not self:
            return root.name() + '.' + self.relative_name(root)
        return self.name()

    def relative_name(self, parent_param):
        parent = self.parent()
        path = [self, ]
        found = False

        while parent:
            if parent == parent_param:
                found = True
                break
            path.append(parent)
            parent = parent.parent()

        if found:
            return '.'.join(map(lambda node: node.name(), reversed(path)))

        raise KeyError('node %s is not a parent of %s' % (parent_param.name(), self.name()))

    #############################################
    # PRIVATE MEMBER METHODS
    #############################################

    def __reset_parent(self, parent):
        """
        Resets the nodes parent.

        Removes node from an already existing parent if necessary and
        emits the parent_changed signal.

        :param parent: new node's parent (must be subclass of AbstractParamNode)
        """
        assert isinstance(parent, AbstractParamNode)

        if parent == self.parent():
            return

        if self.parent():
            self.parent().remove_child(self)

        self._p = parent
        self.parent_changed(parent)

    def __validate_child_name(self, node, new_parent=None):
        """
        Checks whether the given node has a valid name.

        For node names, the following rules oblige
        - node names must be str instances which do not contain any '.' characters
        - node names must be unique, i.e. a sibling node (same parent) with the same name is not allowed

        :param node: a node or str instance to check
        :param new_parent: the new parent of the given node
        :return: the possibly validated node name (str)
        """
        new_parent = self if new_parent is None else new_parent
        name = AbstractParamNode.node_name(node)
        name = name.replace(' ', '_')

        if '.' in name:
            raise ValueError('node names may not contain "." characters!')

        if new_parent and name in new_parent.child_names():
            raise KeyError('node %s already has a child with name %s!' % (new_parent.name(), name))

        return name

    #############################################
    # STATIC METHODS
    #############################################

    @staticmethod
    def node_name(node_or_str):
        """
        Utility function that returns a str object representing a node name.

        :param node_or_str:
        :return:
        """
        if type(node_or_str) == str:
            return node_or_str
        elif isinstance(node_or_str, AbstractParamNode):
            return node_or_str.name()

        raise TypeError('Unexpected type of argument: %s. Supported types: str, AbstractParamNode' % type(node_or_str))


class AbstractParam(AbstractParamNode):
    """
    Base class for param nodes that hold data.

    :ivar _v: instance variable that holds arbitrary data for each node
    """

    def __init__(self, name, parent=None):
        """
        Constructs a new AbstractParam instance.

        :param name:
        :param parent:
        :return:
        """
        AbstractParamNode.__init__(self, name, parent)
        self._v = None

    def unit(self):
        """
        Returns the physical unit of the param instance.

        :return:
        """
        return None

    def value(self):
        """
        Returns the value of the param instance.

        :return:
        """
        return self._v

    def iter_child_values(self, recursive=False):
        """
        Iterates through all child nodes (recursively) and returns their values.

        :param recursive:
        :return:
        """
        for param in self.iter_children(recursive=recursive):
            if isinstance(param, AbstractParam):
                yield param.value()

    #############################################
    # PROTECTED MEMBER METHODS
    #############################################

    def _raw_data(self):
        """
        Returns the node's raw data.

        :return:
        """
        return self._v

    def _raw_child_data(self, recursive=False):
        """
        Returns a dict with relative child names as keys and raw data objects as values.

        :param recursive:
        :return:
        """
        child_data = {}

        if not self.has_children():
            return child_data

        for child in self.iter_children(recursive=recursive):
            if isinstance(child, AbstractParam):
                child_data[child.relative_name(self)] = child._raw_data()

        return child_data

    def _raw_sibling_data(self, name_filter=None):
        """
        Returns a dict with sibling names as keys and raw data objects as values.

        :param name_filter: list of node names for which to collect raw data
        :return:
        """
        sibling_data = {}

        if self.parent() is None:
            return sibling_data

        for sibling in self.iter_siblings():
            if name_filter is not None and sibling.name() not in name_filter:
                continue
            if isinstance(sibling, AbstractParam):
                sibling_data[sibling.name()] = sibling._raw_data()

        return sibling_data
