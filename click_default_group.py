# -*- coding: utf-8 -*-
"""
   click_default_group
   ~~~~~~~~~~~~~~~~~~~

   Define a default subcommand by `default=True`:

   .. sourcecode:: python

      import click
      from click_default_group import DefaultGroup

      @click.group(cls=DefaultGroup)
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

      $ cli.py
      foo
      $ cli.py foo
      foo
      $ cli.py bar
      bar

"""
import click


__all__ = ['DefaultGroup']
__version__ = '1.0'


class DefaultGroup(click.Group):

    def __init__(self, *args, **kwargs):
        super(DefaultGroup, self).__init__(*args, **kwargs)
        self.default_command_name = None
        # To resolve as the default command.
        self.ignore_unknown_options = True

    def command(self, *args, **kwargs):
        default = kwargs.pop('default', False)
        decorator = super(DefaultGroup, self).command(*args, **kwargs)
        if not default:
            # Customized feature not used.
            return decorator
        def _decorator(f):
            cmd = decorator(f)
            if default:
                if self.default_command_name is not None:
                    del self.commands[cmd.name]
                    raise RuntimeError('Default command already defined')
                self.default_command_name = cmd.name
            return cmd
        return _decorator

    def parse_args(self, ctx, args):
        if not args:
            args.insert(0, self.default_command_name)
        return super(DefaultGroup, self).parse_args(ctx, args)

    def get_command(self, ctx, cmd_name):
        if cmd_name not in self.commands:
            # No command name matched.
            ctx.arg0 = cmd_name
            cmd_name = self.default_command_name
        return super(DefaultGroup, self).get_command(ctx, cmd_name)

    def resolve_command(self, ctx, args):
        base = super(DefaultGroup, self)
        cmd_name, cmd, args = base.resolve_command(ctx, args)
        if hasattr(ctx, 'arg0'):
            args.insert(0, ctx.arg0)
        return cmd_name, cmd, args
