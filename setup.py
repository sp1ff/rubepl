from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'description.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name             = 'rubepl',
    version          = '0.0.1',
    description      = 'Playlists utilities',
    long_description = long_description,
    url              = 'https://github.com/pypa/rubepl',
    author           = 'Michael',
    author_email     = 'sp1ff@pobox.com',
    license          = 'GPL',
    # Cf. https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers      = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Python Modules',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Programming Language :: Python :: 3.4',
    ],
    keywords         = 'playlists music audio',
    # You can just specify the packages manually here if your project
    # is simple. Or you can use find_packages().
    packages         = find_packages(exclude=['contrib', 'docs', 'test*']),

    # TODO: Clean this up...
    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    # install_requires=['peppercorn'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    # extras_require={
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={
    #     'description': ['description.rst'],
    # },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference
    # to the"scripts" keyword. Entry points provide cross-platform
    # support and allow pip to create the appropriate form of
    # executable for the target platform.
    entry_points     = {
        'console_scripts': [
            'rubepl=rubepl:main',
        ],
    },
    test_suite      = 'test'
)
