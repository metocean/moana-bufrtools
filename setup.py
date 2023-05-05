import os
import re
from setuptools import find_packages
from codecs import open

from setuptools import dist

dist.Distribution().fetch_build_eggs(["numpy"])
from numpy.distutils.core import setup
from numpy.distutils.misc_util import Configuration

import GTS_encode

NAME = "GTS_encode"

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
]


def getreq(fpath):
    return read(fpath).splitlines()


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def ext_configuration(parent_package="", top_path=None):
    config = Configuration("", "", "")
    config.add_data_files(
        "LICENSE",
    )
    return config


install_requires = [
    "matplotlib",
    "python-dateutil",
    "sortedcontainers",
    "eccodes",
    "eccodes-python",
    "xarray",
    "dask",
    "netCDF4",
    "bottleneck",
    "numpy",
    "pandas",
]


setup_requirements = ["pytest-runner"]
kwargs = ext_configuration(top_path="").todict()

setup(
    name=NAME,
    version=GTS_encode.__version__,
    description=GTS_encode.__description__,
    long_description=read("README.md"),
    long_description_content_type="text/x-rst",
    keywords=GTS_encode.__keywords__,
    author=GTS_encode.__author__,
    author_email=GTS_encode.__contact__,
    license="MIT license",
    packages=find_packages(),
    platforms=["any"],
    install_requires=install_requires,
    setup_requires=setup_requirements,
    test_require=getreq('requirements/tests.txt')
    test_suite='pytest',
    python_requires=">=3.0",
    classifiers=CLASSIFIERS,
    zip_safe=False,
    **kwargs
)
