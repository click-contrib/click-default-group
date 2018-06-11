# -*- coding: utf-8 -*-
import click
from click.testing import CliRunner
import pytest

from click_default_group import DefaultGroup


@click.group(cls=DefaultGroup, default='foo', invoke_without_command=True)
@click.option('--group-only', is_flag=True)
def cli(group_only):
    # Called if invoke_without_command=True.
    if group_only:
        click.echo('--group-only passed.')


@cli.command()
@click.option('--foo', default='foo')
def foo(foo):
    click.echo(foo)


@cli.command()
def bar():
    click.echo('bar')


r = CliRunner()


def test_default_command_with_arguments():
    assert r.invoke(cli, ['--foo', 'foooo']).output == 'foooo\n'
    assert 'no such option' in r.invoke(cli, ['-x']).output


def test_group_arguments():
    assert r.invoke(cli, ['--group-only']).output == '--group-only passed.\n'


def test_explicit_command():
    assert r.invoke(cli, ['foo']).output == 'foo\n'
    assert r.invoke(cli, ['bar']).output == 'bar\n'


def test_set_ignore_unknown_options_to_false():
    with pytest.raises(ValueError):
        DefaultGroup(ignore_unknown_options=False)


def test_default_if_no_args():
    cli = DefaultGroup()

    @cli.command()
    @click.argument('foo', required=False)
    @click.option('--bar')
    def foobar(foo, bar):
        click.echo(foo)
        click.echo(bar)

    cli.set_default_command(foobar)
    assert r.invoke(cli, []).output.startswith('Usage:')
    assert r.invoke(cli, ['foo']).output == 'foo\n\n'
    assert r.invoke(cli, ['foo', '--bar', 'bar']).output == 'foo\nbar\n'
    cli.default_if_no_args = True
    assert r.invoke(cli, []).output == '\n\n'


def test_format_commands():
    help = r.invoke(cli, ['--help']).output
    assert 'foo*' in help
    assert 'bar*' not in help
    assert 'bar' in help


def test_deprecation():
    # @cli.command(default=True) has been deprecated since 1.2.
    cli = DefaultGroup()
    pytest.deprecated_call(cli.command, default=True)


if __name__ == '__main__':
    cli()
