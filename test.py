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
    assert 'no such option' in r.invoke(cli, ['-x']).output.lower()


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


def test_chain_unknown_command_terminates(monkeypatch):
    @click.group(cls=DefaultGroup, default='foo', default_if_no_args=True,
                 chain=True)
    def chained():
        pass

    @chained.command()
    def foo():
        click.echo('foo')

    resolve_command = chained.resolve_command
    resolutions = [0]

    def bounded_resolve(ctx, args):
        resolutions[0] += 1
        assert resolutions[0] < 10, 'Default command resolution did not progress'
        return resolve_command(ctx, args)

    monkeypatch.setattr(chained, 'resolve_command', bounded_resolve)
    result = r.invoke(chained, ['unknown'])
    assert result.exit_code == 2
    assert 'no such command' in result.output.lower()
    assert 'unknown' in result.output
    assert resolutions[0] == 2


def test_chain_default_argument_then_explicit_command():
    @click.group(cls=DefaultGroup, default='foo', chain=True)
    def chained():
        pass

    @chained.command()
    @click.argument('value')
    def foo(value):
        click.echo(value)

    @chained.command()
    def bar():
        click.echo('bar')

    for _ in range(2):
        result = r.invoke(chained, ['value', 'bar', 'bar'])
        assert result.exit_code == 0, result.output
        assert result.output == 'value\nbar\nbar\n'


if __name__ == '__main__':
    cli()
