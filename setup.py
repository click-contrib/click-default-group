# -*- coding: utf-8 -*-
import re

from setuptools import setup
from setuptools.command.test import test


with open('click_default_group.py') as f:
    version = re.search(r'__version__\s*=\s*\'(.+?)\'', f.read()).group(1)
assert version


# Use pytest instead.
def run_tests(self):
    raise SystemExit(__import__('pytest').main(['-v']))
test.run_tests = run_tests


setup(
    name='click-default-group',
    version=version,
    author='Heungsub Lee',
    author_email='sub@subl.ee',
    description=('Extends click.Group to invoke a '
                 'command without explicit subcommand name'),
    url='https://github.com/sublee/click-default-group/',
    platforms='any',
    py_modules=['click_default_group'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    install_requires=['click'],
    tests_require=['pytest'],
    test_suite='...',
)
