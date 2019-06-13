Click Default Group
===================

`DefaultGroup` is a sub class of [`click.Group`](http://click.pocoo.org/6/api/#click.Group).  But it invokes a default
subcommand instead of showing a help message when a subcommand is not passed.

[![Build Status](https://img.shields.io/travis/click-contrib/click-default-group.svg)](https://travis-ci.org/click-contrib/click-default-group)
[![Coverage Status](https://img.shields.io/coveralls/click-contrib/click-default-group.svg)](https://coveralls.io/r/click-contrib/click-default-group)

Usage
-----

Define a default subcommand by `default=NAME`:

```python
import click
from click_default_group import DefaultGroup

@click.group(cls=DefaultGroup, default='foo', default_if_no_args=True)
def cli():
    pass

@cli.command()
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

- Click-7.0
- Click-6.x
- Click-5.1
- Click-5.0
- Click-4.1
- Click-4.0

See the [latest build status](https://travis-ci.org/click-contrib/click-default-group)
at Travis CI.

Licensing
---------

Written by [Heungsub Lee], and distributed under the [BSD 3-Clause] license.

[Heungsub Lee]: http://subl.ee/
[BSD 3-Clause]: http://opensource.org/licenses/BSD-3-Clause
