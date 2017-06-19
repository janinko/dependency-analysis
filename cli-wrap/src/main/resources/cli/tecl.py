#!/usr/bin/env python3
import click

@click.command()
def hello():
    print('Hello World!')

@click.group()
def cli():
    pass

@click.command()
def initdb():
    """barfoo"""

    print('Initialized the database')

@click.command()
def dropdb():
    "foobar"

    print('Dropped the database')


def main():
    cli.add_command(initdb)
    cli.add_command(dropdb)
    cli()

if __name__ == '__main__':
    main()
