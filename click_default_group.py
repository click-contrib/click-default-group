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

import typing as t
import warnings

import click

__all__ = ['DefaultGroup']
__version__ = '1.2.4'


class DefaultGroup(click.Group):
    """Invokes a subcommand marked with `default=True` if any subcommand not
    chosen.

    :param default_if_no_args: resolves to the default command if no arguments
                               passed.

    """

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        # To resolve as the default command.
        if not kwargs.get('ignore_unknown_options', True):
            raise ValueError('Default group accepts unknown options')
        self.ignore_unknown_options = True
        self.default_cmd_name = kwargs.pop('default', None)
        self.default_if_no_args = kwargs.pop('default_if_no_args', False)
        super().__init__(*args, **kwargs)

    def set_default_command(self, command: t.Any) -> None:
        """Sets a command function as the default command."""
        cmd_name = command.name
        self.add_command(command)
        self.default_cmd_name = cmd_name

    def parse_args(self, ctx: click.core.Context, args: t.List[str]) -> t.List[str]:
        if not args and self.default_if_no_args:
            args.insert(0, self.default_cmd_name)
        return super().parse_args(ctx, args)

    def get_command(
        self, ctx: click.core.Context, cmd_name: str
    ) -> t.Optional[click.core.Command]:
        if cmd_name not in self.commands:
            # No command name matched.
            ctx.arg0 = cmd_name  # type: ignore
            cmd_name = self.default_cmd_name
        return super().get_command(ctx, cmd_name)

    def resolve_command(
        self, ctx: click.core.Context, args: t.List[str]
    ) -> t.Tuple[t.Optional[str], t.Optional[click.core.Command], t.List[str]]:
        cmd_name, cmd, args = super().resolve_command(ctx, args)
        if cmd and hasattr(ctx, 'arg0'):
            args.insert(0, ctx.arg0)
            cmd_name = cmd.name
        return cmd_name, cmd, args

    def format_commands(
        self, ctx: click.core.Context, formatter: click.formatting.HelpFormatter
    ) -> None:
        new_formatter = DefaultCommandFormatter(self, formatter, mark="*")
        return super().format_commands(ctx, new_formatter)

    @t.overload
    def command(self, __func: t.Callable[..., t.Any]) -> click.core.Command: ...

    @t.overload
    def command(
        self, *args: t.Any, **kwargs: t.Any
    ) -> t.Callable[[t.Callable[..., t.Any]], click.core.Command]: ...

    def command(
        self, *args: t.Any, **kwargs: t.Any
    ) -> t.Union[
        t.Callable[[t.Callable[..., t.Any]], click.core.Command], click.core.Command
    ]:
        default = kwargs.pop("default", False)
        decorator: t.Callable[[t.Callable[..., t.Any]], click.core.Command] = super().command(*args, **kwargs)
        if not default:
            return decorator
        warnings.warn('Use default param of DefaultGroup or '
                      'set_default_command() instead', DeprecationWarning)

        def _decorator(f: t.Callable[..., t.Any]) -> click.core.Command:
            cmd: click.core.Command = decorator(f)
            self.set_default_command(cmd)
            return cmd

        return _decorator


class DefaultCommandFormatter(click.formatting.HelpFormatter):
    """Wraps a formatter to mark a default command."""

    def __init__(
        self,
        group: DefaultGroup,
        formatter: click.formatting.HelpFormatter,
        mark: str = "*",
    ):
        self.group = group
        self.formatter = formatter
        self.mark = mark

        super().__init__()

    def __getattr__(self, attr: str) -> t.Any:
        return getattr(self.formatter, attr)

    def write_dl(
        self, rows: t.Sequence[t.Tuple[str, str]], *args: t.Any, **kwargs: t.Any
    ) -> None:
        rows_: t.List[t.Tuple[str, str]] = []
        for cmd_name, text in rows:
            if cmd_name == self.group.default_cmd_name:
                rows_.insert(0, (cmd_name + self.mark, text))
            else:
                rows_.append((cmd_name, text))
        return self.formatter.write_dl(rows_, *args, **kwargs)
