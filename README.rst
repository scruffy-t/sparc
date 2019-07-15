sparc
=====

*sparc* helps you create user interfaces (UI) for editing data structures. No matter if you want to
write a UI for an existing data structure or you start from scratch, *sparc* can speed up your work.

Check out the `Examples`_ section to see what *sparc* can do for you.

Currently, *sparc* only supports UI generation for the `Qt <https://www.qt.io>`_ framework via
`PyQt <https://riverbankcomputing.com/software/pyqt/intro>`_ (currently PyQt5), but the *sparc* core
is written in a generic way, so that it is rather easy to extend *sparc* for other GUI frameworks
such as `wxWidgets <https://www.wxwidgets.org>`_.

Dependencies
============

*sparc* is completely written in the Python programming language and has no dependencies. ::

    Python (>= 3.6)

Optionally, if you want to use the ``gui`` module, the following dependencies exist ::

    PyQt5

Installation
============

The easiest way to install or update sparc is using **pip** (or **pipenv**) ::

    pip install -U sparc

If you want to install the latest version of *sparc*, just clone the github repository and install
using setuptools ::

    git clone git@github.com:tschruff/sparc.git
    cd sparc
    python3 setup.py install

If you want to develop with *sparc* you may install using the ``develop`` command instead of
the ``install`` command.

Examples
========

The first example shows how to create a parameter tree from scratch.

.. code-block:: python

    from sparc import *

    # first, we need a group node
    # the root of our parameter collection
    p = ParamGroupNode('calc')

    # add a parameter node
    c = ParamNode('m', 5.0, float)
    p.add_child(c)

    # add another node by providing the
    # constructor arguments directly to
    # the add_child method
    p.add_child('a', 2.0, float)

    # or add a whole bunch of nodes
    p.add_children([
        dict(name='A', value=4.0, type=float),
        dict(name='∆', value='=F/A', type=float),
        dict(name='l', value='=A**0.5', type=float)
    ])

    # ∆ and l are expression nodes
    # they work like in Excel, i.e. the '= ...' notation
    # and can use sibling nodes as variables

    # retrieving node values is as simple as
    value = p['l'].value()

If you have an existing data structure, *sparc* works a little bit different. Let's assume there is a
data structure defined in some external module (so you have no chance to change it's definition).

.. code-block:: python

    class Data(object):

        def __init__(self, f, b):
            self._foo = f
            self._bar = b

        def foo(self):
            return self._foo

        def set_foo(self, f):
            self._foo = f

        def bar(self):
            return self._bar

        def set_bar(self, b):
            self._bar = b

You can now use *sparc* to wrap the getter and setter functions and create a parameter tree.

.. code-block:: python

    from sparc import *

    unbound_param = ParamGroup('data')
    unbound_param.add_children([
        dict(name='foo', type=int, fget=Data.foo, fset=Data.set_foo),
        dict(name='bar', type=float, fget=Data.bar, fset=Data.set_bar)
    ])

    d = Data(4, 6.5)

    # returns True
    unbound_param['foo'].is_unbound()

    # you must provide a Data instance to obtain it's value
    unbound_param['foo'].value(obj=d)

Alternatively, you can wrap getter and setter methods.

.. code-block:: python

    d = Data(4, 6.5)

    bound_param = ParamGroup('data')
    bound_param.add_children([
        dict(name='foo', type=int, fget=d.foo, fset=d.set_foo),
        dict(name='bar', type=float, fget=d.bar, fset=d.set_bar)
    ])

    # returns False
    unbound_param['foo'].is_unbound()

    # no nee to provide the Data instance for bound parameters
    bound_param['foo'].value()

Developers
----------

*sparc* is developed by me, Tobias Schruff <tobias.schruff@gmail.com>. Feel free to contact me for bugs or feature
requests.
