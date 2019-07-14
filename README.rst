sparc
=====

*sparc* (acronym for Scientific PARameter Collection) is a Python module that provides classes
to easily **create**, **edit**, **visualize**, and **serialize** parameter structures.

In the world of *sparc*, a parameter is a name-value pair. Parameters can be nested and depend
on other parameter values, thereby emulating spreadsheet-like behavior.

Check out the `Examples`_ section to see what you can do with *sparc*.

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


Examples
========

The first example shows how to create a parameter tree.

.. code-block::

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


Developers
----------

*sparc* is developed by me, Tobias Schruff <tobias.schruff@gmail.com>. Feel free to contact me for bugs or feature
requests.
