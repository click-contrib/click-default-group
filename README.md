Click Default Group
===================

`DefaultGroup` is a sub class of [`click.Group`]
(http://click.pocoo.org/6/api/#click.Group).  But it invokes a default
subcommand instead of showing a help message when a subcommand is not passed.

[![Build Status]
(https://travis-ci.org/sublee/click-default-group.svg?branch=master)]
(https://travis-ci.org/sublee/click-default-group)
[![Coverage Status]
(https://coveralls.io/repos/sublee/click-default-group/badge.svg?branch=master)]
(https://coveralls.io/r/sublee/click-default-group)

Usage
-----

Define a default subcommand by `default=True`:

```python
import click
from click_default_group import DefaultGroup

@click.group(cls=DefaultGroup, default_if_no_args=True)
def cli():
    pass

@cli.command(default=True)
def foo():
    click.echo('foo')

@cli.command()
def bar():
    click.echo('bar')
```

Then you can invoke that without explicit subcommand name:

```console
$ cli.py --help
Usage: cli.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help    Show this message and exit.

Command:
  foo*
  bar

$ cli.py
foo
$ cli.py foo
foo
$ cli.py bar
bar
```

Compatibility
-------------

`click-default-group` is compatible with these Click versions:

- Click-6.2
- Click-6.1
- Click-6.0
- Click-5.1
- Click-5.0
- Click-4.1
- Click-4.0

See the [latest build status](https://travis-ci.org/sublee/click-default-group)
at Travis CI.

Licensing
---------

Written by [Heungsub Lee], and distributed under the [BSD 3-Clause] license.

[Heungsub Lee]: http://subl.ee/
[BSD 3-Clause]: http://opensource.org/licenses/BSD-3-Clause
