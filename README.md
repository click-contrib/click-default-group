Click Default Group
===================

[![Test Status](https://github.com/click-contrib/click-default-group/actions/workflows/test.yaml/badge.svg)](https://github.com/click-contrib/click-default-group/actions/workflows/test.yaml)

`DefaultGroup` is a subclass of
[`click.Group`](https://click.pocoo.org/6/api/#click.Group).  But it invokes
the default subcommand instead of showing a help message when a subcommand is
not passed.

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

- Click-8.x
- Click-7.x
- Click-6.x
- Click-5.x
- Click-4.x

Licensing
---------

Written by [Heungsub Lee], and distributed under the [BSD 3-Clause] license.

[Heungsub Lee]: https://subl.ee/
[BSD 3-Clause]: https://opensource.org/licenses/BSD-3-Clause
