from setuptools import setup


def readme():
    with open('README.rst', 'r') as f:
        return f.read()


setup(
    name='sparc',
    version='0.1.0a1',
    description='A framework to create, edit, visualize, and serialize scientific parameter collections',
    long_description=readme(),

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],

    keywords='scientific parameters',
    url='https://github.com/scruffy-t/sparc',
    author='Tobias Schruff',
    author_email='tobias.schruff@gmail.com',
    license='BSD',
    packages=['sparc'],
    install_requires=['pint'],

    # we use "nose" for tests
    # $ python setup.py test
    # to execute the test suite
    test_suite='nose.collector',
    tests_require=['nose'],

    include_package_data=True,
    zip_safe=False
)
