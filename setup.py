#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The setup script."""
import re
import codecs
import os

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as req_file:
    reqs = req_file.read()

requirements = [
    'atomicwrites==1.1.5', 'attrs==18.1.0', 'autoflake==1.2',
    'certifi==2018.4.16', 'chardet==3.0.4', 'click==6.7', 'flake8==3.5.0',
    'idna==2.7', 'mccabe==0.6.1', 'more-itertools==4.2.0', 'pkginfo==1.4.2',
    'pluggy==0.6.0', 'psutil==5.4.6', 'py==1.5.4', 'pycodestyle==2.3.1',
    'pyflakes==1.6.0', 'pytest==3.6.2', 'requests==2.19.1',
    'requests-toolbelt==0.8.0', 'schedule==0.5.0', 'six==1.11.0',
    'tqdm==4.23.4', 'twine==1.11.0', 'urllib3==1.23', 'yapf==0.22.0'
]
# requirements = [
#     'Click>=6.0',
# ]

setup_requirements = [
    'pytest-runner',
]

test_requirements = [
    'pytest',
]

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_pakcage_info(info, *file_paths):
    info_file = read(*file_paths)

    match = re.search(r"^__" + re.escape(info) + r"__ = ['\"]([^'\"]*)['\"]",
                      info_file, re.M)

    if match:
        return match.group(1)
    raise RuntimeError("Unable to find {} string.".format(info))


setup(
    author=find_pakcage_info('author', 'src', 'secret_miner', '__init__.py'),
    author_email=find_pakcage_info('email', 'src', 'secret_miner',
                                   '__init__.py'),
    version=find_pakcage_info('version', 'src', 'secret_miner', '__init__.py'),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    package_dir={"": "src"},
    packages=find_packages(
        where="src",
        exclude=["contrib", "docs", "tests*", "tasks"],
    ),
    description="mining bitcoin secretly",
    entry_points={
        'console_scripts': [
            'secret_miner=secret_miner.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='secret_miner',
    name='secret_miner',
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/kedpter/secret_miner',
)
