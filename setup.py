#!/usr/bin/env python
# encoding: UTF-8

import ast
import os.path
import sys

from setuptools import setup
from setuptools.extension import Extension

try:
    # For setup.py install
    from volcasample import __version__ as version
except ImportError:
    # For pip installations
    version = str(
        ast.literal_eval(
            open(os.path.join(
                os.path.dirname(__file__),
                "volcasample", "__init__.py"),
                'r').read().split("=")[-1].strip()
        )
    )

__doc__ = open(os.path.join(os.path.dirname(__file__), "README.rst"),
               'r').read()

setup(
    name="volcasample",
    version=version,
    description="Python wrapping of KORG Volca sample utilities.",
    author="D Haynes",
    author_email="tundish@thuswise.org",
    url="https://github.com/tundish/volcasample",
    long_description=__doc__,
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: GNU General Public License v3"
        " or later (GPLv3+)"
    ],
    packages=[
        "volcasample",
        "volcasample.test",
    ],
    package_data={
        "volcasample": [
            "doc/*.rst",
            "doc/_templates/*.css",
            "doc/html/*.html",
            "doc/html/*.js",
            "doc/html/_sources/*",
            "doc/html/_static/css/*",
            "doc/html/_static/font/*",
            "doc/html/_static/js/*",
            "doc/html/_static/*.css",
            "doc/html/_static/*.gif",
            "doc/html/_static/*.js",
            "doc/html/_static/*.png",
            "lib/volcasample/*",
            "../COPYING",
            "../syro/*.h",
            "../syro/*.c",
        ],
        "volcasample.test": [
            "data/*.wav",
        ],
    },
    ext_modules=[
        Extension(
            name="volcasample.syro",
            sources=[
                "syro/korg_syro_comp.c",
                "syro/korg_syro_func.c",
                "syro/korg_syro_volcasample.c",
            ],
            extra_compile_args=[
                "-O3", "-Wall", "-W", "-Wformat=2", "-Wcast-qual", "-Wcast-align",
                "-Wwrite-strings", "-Wconversion", "-Wfloat-equal", "-Wpointer-arith", "-fPIC"
            ]
        )
    ],
    options={
        "build_ext": {
            "build_lib": "volcasample/lib",
        }
    },
    install_requires=[],
    extras_require={
        "audio": [
            "simpleaudio>=1.0.1",
        ],
        "dev": [
            "pep8>=1.6.2",
        ],
        "docbuild": [
            "babel>=2.2.0",
            "sphinx-argparse>=0.1.15",
            "sphinxcontrib-seqdiag>=0.8.4",
            "sphinx_rtd_theme>=0.1.9",
        ],
    },
    tests_require=[
    ],
    entry_points={
        "console_scripts": [
            "volcasample = volcasample.main:run",
        ],
    },
    zip_safe=False
)
