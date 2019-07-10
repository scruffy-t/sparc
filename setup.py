from setuptools import setup
from sparc import __version__


def readme():
    with open('README.rst', 'r') as f:
        return f.read()


setup(
    name='sparc',
    version=__version__,
    description='A framework to create, edit, visualize, and serialize scientific parameter collections',
    long_description=readme(),

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],

    keywords='scientific parameters GUI',
    url='https://github.com/tschruff/sparc',
    author='Tobias Schruff',
    author_email='tobias.schruff@gmail.com',
    license='BSD',
    packages=['sparc'],
    # install_requires=['pint'],

    # $ python setup.py test
    # to execute the test suite
    test_suite='tests',

    include_package_data=False,
    zip_safe=False
)
