"""
   click_default_group
   ~~~~~~~~~~~~~~~~~~~

   Define a default subcommand by `default=True`:

   .. sourcecode:: python

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

   Then you can invoke that without explicit subcommand name:

   .. sourcecode:: console

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

"""
from __future__ import annotations

import warnings
from typing import Any, Callable, List, Optional, Sequence, Tuple

import click


__all__ = ['DefaultGroup']
__version__ = '1.2.4'


class DefaultGroup(click.Group):
    """Invokes a subcommand marked with `default=True` if any subcommand not
    chosen.

    :param default_if_no_args: resolves to the default command if no arguments
                               passed.

    """

    ignore_unknown_options: bool
    default_cmd_name: Optional[str]
    default_if_no_args: bool

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # To resolve as the default command.
        if not kwargs.get('ignore_unknown_options', True):
            raise ValueError('Default group accepts unknown options')
        self.ignore_unknown_options = True
        self.default_cmd_name = kwargs.pop('default', None)
        self.default_if_no_args = kwargs.pop('default_if_no_args', False)
        super(DefaultGroup, self).__init__(*args, **kwargs)

    def set_default_command(self, command: click.Command) -> None:
        """Sets a command function as the default command."""
        cmd_name = command.name
        self.add_command(command)
        self.default_cmd_name = cmd_name

    def parse_args(self, ctx: click.Context, args: List[str]) -> List[str]:
        if not args and self.default_if_no_args:
            args.insert(0, self.default_cmd_name)  # type: ignore[arg-type]
        return super(DefaultGroup, self).parse_args(ctx, args)

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        if cmd_name not in self.commands:
            # No command name matched.
            ctx.arg0 = cmd_name  # type: ignore[attr-defined]
            cmd_name = self.default_cmd_name  # type: ignore[assignment]
        return super(DefaultGroup, self).get_command(ctx, cmd_name)

    def resolve_command(
        self, ctx: click.Context, args: List[str]
    ) -> Tuple[Optional[str], Optional[click.Command], List[str]]:
        base = super(DefaultGroup, self)
        cmd_name, cmd, args = base.resolve_command(ctx, args)
        if hasattr(ctx, 'arg0'):
            args.insert(0, ctx.arg0)  # type: ignore[attr-defined]
            cmd_name = cmd.name  # type: ignore[union-attr, assignment]
        return cmd_name, cmd, args

    def format_commands(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        formatter = DefaultCommandFormatter(self, formatter, mark='*')  # type: ignore[assignment]
        return super(DefaultGroup, self).format_commands(ctx, formatter)

    def command(self, *args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], click.Command]:
        default = kwargs.pop('default', False)
        decorator = super(DefaultGroup, self).command(*args, **kwargs)
        if not default:
            return decorator  # type: ignore[return-value]
        warnings.warn('Use default param of DefaultGroup or '
                      'set_default_command() instead', DeprecationWarning)

        def _decorator(f: Callable[..., Any]) -> click.Command:
            cmd = decorator(f)
            self.set_default_command(cmd)
            return cmd

        return _decorator


class DefaultCommandFormatter(object):
    """Wraps a formatter to mark a default command."""

    def __init__(self, group: DefaultGroup, formatter: click.HelpFormatter, mark: str = '*') -> None:
        self.group = group
        self.formatter = formatter
        self.mark = mark

    def __getattr__(self, attr: str) -> Any:
        return getattr(self.formatter, attr)

    def write_dl(self, rows: Sequence[Tuple[str, str]], *args: Any, **kwargs: Any) -> Any:
        rows_: List[Tuple[str, str]] = []
        for cmd_name, help in rows:
            if cmd_name == self.group.default_cmd_name:
                rows_.insert(0, (cmd_name + self.mark, help))
            else:
                rows_.append((cmd_name, help))
        return self.formatter.write_dl(rows_, *args, **kwargs)
