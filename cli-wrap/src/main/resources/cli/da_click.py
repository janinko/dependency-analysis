#!/usr/bin/env python3
import click
import re

class AliasGroup(click.Group):

    def __init__(self, name=None, **attrs):
        click.Group.__init__(self, name, **attrs)
        self.aliases = {}

    def add_alias(self, cmd):
        name = cmd.name
        if name is None:
            raise TypeError('Command has no name.')
        self.aliases[name] = True

    def alias_group(self, *args, **kwargs):
        def decorator(f):
            cmd = click.group(*args, **kwargs)(f)
            self.add_command(cmd)
            self.add_alias(cmd)
            return cmd
        return decorator

    def list_commands(self, ctx):
        names = []
        for name in self.commands.keys():
            if name not in self.aliases:
                names.append(name)
        return { name: self.commands[name] for name in names }


class GAVType(click.ParamType):
    name = 'gav'
    pattern = re.compile("^[^:]+:[^:]+:[^:]+$")

    def convert(self, value, param, ctx):
        if not self.pattern.match(value):
            self.fail('%s is not a valid groupid:artifactid:version' % value, param, ctx)
        return value

GAV = GAVType()

