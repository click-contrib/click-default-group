Click Default Group
===================

A default group invokes a default subcommand if no subcommand passed.

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

Licensing
---------

Written by [Heungsub Lee], and distributed under the [BSD 3-Clause] license.

[Heungsub Lee]: http://subl.ee/
[BSD 3-Clause]: http://opensource.org/licenses/BSD-3-Clause
