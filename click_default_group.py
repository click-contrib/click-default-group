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

    def __init__(self, *args, **kwargs):
        # To resolve as the default command.
        if not kwargs.get('ignore_unknown_options', True):
            raise ValueError('Default group accepts unknown options')
        self.ignore_unknown_options = True
        self.default_cmd_name = kwargs.pop('default', None)
        self.default_if_no_args = kwargs.pop('default_if_no_args', False)
        super(DefaultGroup, self).__init__(*args, **kwargs)

    def set_default_command(self, command):
        """Sets a command function as the default command."""
        cmd_name = command.name
        self.add_command(command)
        self.default_cmd_name = cmd_name

    def parse_args(self, ctx, args):
        if not args and self.default_if_no_args:
            args.insert(0, self.default_cmd_name)

        if ctx.resilient_parsing:
            return super(DefaultGroup, self).parse_args(ctx, args)

        # fixup to allow help work for subcommands
        test_ctx = self.make_context(ctx.info_name, ctx.args, resilient_parsing=True)
        rest = super(DefaultGroup, self).parse_args(test_ctx, args[:])

        help_options = self.get_help_option_names(ctx)
        if help_options and self.add_help_option and rest and any(s in help_options for s in rest):
            return super(DefaultGroup, self).parse_args(ctx, args)

        save_allow_interspersed_args = ctx.allow_interspersed_args
        ctx.allow_interspersed_args = True
        rest = super(DefaultGroup, self).parse_args(ctx, args)
        ctx.allow_interspersed_args = save_allow_interspersed_args

        if not rest and (ctx.protected_args or ['a'])[0][:1].isalnum() and not self.default_if_no_args:
            pass  # Don't inject default_cmd_name if no command or command-specific options passed
        elif not ctx.protected_args:
            ctx.protected_args = [self.default_cmd_name]
        else:
            cmd_name = ctx.protected_args[0]
            cmd = self.get_command(ctx, cmd_name)
            if cmd is None and ctx.token_normalize_func is not None:
                cmd_name = ctx.token_normalize_func(cmd_name)
                cmd = self.get_command(ctx, cmd_name)
            if cmd is None:
                ctx.protected_args.insert(0, self.default_cmd_name)
        return rest

    def format_commands(self, ctx, formatter):
        formatter = DefaultCommandFormatter(self, formatter, mark='*')
        return super(DefaultGroup, self).format_commands(ctx, formatter)

    def command(self, *args, **kwargs):
        default = kwargs.pop('default', False)
        decorator = super(DefaultGroup, self).command(*args, **kwargs)
        if not default:
            return decorator
        warnings.warn('Use default param of DefaultGroup or '
                      'set_default_command() instead', DeprecationWarning)

        def _decorator(f):
            cmd = decorator(f)
            self.set_default_command(cmd)
            return cmd

        return _decorator


class DefaultCommandFormatter(object):
    """Wraps a formatter to mark a default command."""

    def __init__(self, group, formatter, mark='*'):
        self.group = group
        self.formatter = formatter
        self.mark = mark

    def __getattr__(self, attr):
        return getattr(self.formatter, attr)

    def write_dl(self, rows, *args, **kwargs):
        rows_ = []
        for cmd_name, help in rows:
            if cmd_name == self.group.default_cmd_name:
                rows_.insert(0, (cmd_name + self.mark, help))
            else:
                rows_.append((cmd_name, help))
        return self.formatter.write_dl(rows_, *args, **kwargs)
