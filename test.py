# -*- coding: utf-8 -*-
import click
from click.testing import CliRunner
import pytest

from click_default_group import DefaultGroup


@pytest.fixture
def cli_group():
    @click.group(cls=DefaultGroup, default='foo')
    @click.option('--verbose', is_flag=True)
    def cli(verbose):
        if verbose:
            click.echo('Verbose!')

    @cli.command()
    @click.option('--foo_opt')
    @click.argument('foo_arg', required=False)
    def foo(foo_opt, foo_arg):
        click.echo('foo exec')
        if foo_opt:
            click.echo(f'foo_opt={foo_opt}')
        if foo_arg:
            click.echo(f'foo_arg={foo_arg}')

    @cli.command()
    def bar():
        click.echo('bar exec')

    return cli

@pytest.fixture
def cli_group_with_default(cli_group: DefaultGroup):
    cli_group.default_if_no_args = True
    return cli_group

r = CliRunner()

def test_normal_calling(cli_group: DefaultGroup):
    assert r.invoke(cli_group, []).output.startswith('Usage:')
    assert r.invoke(cli_group, ['foo']).output == 'foo exec\n'
    assert r.invoke(cli_group, ['foo', '--foo_opt', 'opt']).output == 'foo exec\nfoo_opt=opt\n'

def test_explicit_command(cli_group_with_default: DefaultGroup):
    assert r.invoke(cli_group_with_default, ['foo']).output == 'foo exec\n'
    assert r.invoke(cli_group_with_default, ['bar']).output == 'bar exec\n'

def test_default_command_with_arguments():
    assert r.invoke(cli, ['--foo', 'foooo']).output == 'foooo\n'
    assert 'no such option' in r.invoke(cli, ['-x']).output.lower()

def test_default_if_no_args(cli_group_with_default: DefaultGroup):
    assert r.invoke(cli_group_with_default, []).output == 'foo exec\n'

def test_default_command_with_arguments(cli_group_with_default: DefaultGroup):
    assert r.invoke(cli_group_with_default, ['--foo_opt', 'opt']).output == 'foo exec\nfoo_opt=opt\n'
    assert 'No such option' in r.invoke(cli_group_with_default, ['-x']).output

def test_group_arguments(cli_group: DefaultGroup):
    assert 'Error: Missing command' in r.invoke(cli_group, ['--verbose']).output

def test_group_arguments_without_cmd(cli_group: DefaultGroup):
    cli_group.invoke_without_command = True
    assert r.invoke(cli_group, ['--verbose', '--foo_opt=123']).output == 'Verbose!\nfoo exec\nfoo_opt=123\n'
    assert r.invoke(cli_group, ['--verbose']).output == 'Verbose!\n'

def test_group_arguments_if_no_args(cli_group: DefaultGroup):
    cli_group.default_if_no_args = True
    assert r.invoke(cli_group, ['--verbose', '--foo_opt=123']).output == 'Verbose!\nfoo exec\nfoo_opt=123\n'
    assert r.invoke(cli_group, ['--verbose']).output == 'Verbose!\nfoo exec\n'

def test_set_ignore_unknown_options_to_false():
    with pytest.raises(ValueError):
        DefaultGroup(ignore_unknown_options=False)

def test_format_commands(cli_group_with_default: DefaultGroup):
    help = r.invoke(cli_group_with_default, ['--help']).output
    assert 'foo*' in help
    assert 'bar*' not in help
    assert 'bar' in help

def test_deprecation():
    # @cli.command(default=True) has been deprecated since 1.2.
    cli = DefaultGroup()
    pytest.deprecated_call(cli.command, default=True)


if __name__ == '__main__':
    cli_group()
