#!/usr/bin/env python3
import os
import json
import click
from da_client import DAClient
from da_api import Blacklist
import da_click

cmd_folder = os.path.dirname(os.path.realpath(__file__))

with open(cmd_folder+'/config.json') as config_file:
    config = json.load(config_file)

da_server_raw = os.getenv('DA_SERVER', config["daServer"])

if (da_server_raw == ""):
    print("Please configure DA server by command $ export DA_SERVER=your.adress")
    print("or by filling address in configuration file (config.json).")
    exit()
    
da = DAClient(da_server_raw, config["keycloakServer"], config["keycloakClientId"],
        config["keycloakRealm"])

blacklist = Blacklist(da)

@click.group(cls=da_click.AliasGroup)
def main():
    """This CLI tool is used for communication with Dependency Analyzer, a service which provides information about built artifacts and analyse projects dependencies.

    This tool has two main usages: black & white lists of artifacts and dependency reports."""
    pass

@main.group("blacklist", short_help="Check, list and mange blacklisted artifacts.")
def cli_blacklist():
    """An artifact (groupId:artifactId:version) can be either whitelisted in
    some products, blacklisted in all product or graylisted.

    Each whitelisted artifact is whitelisted in one or more product versions.
    Each product can also be in one of the following states: supported,
    superseded, unsupported or unknown. Whitelisted artifacts are in their
    -redhat version.

    Blaclisted artifact is not associated with any product. When artifact is
    blacklisted, it is blacklisted across all products. Blacklisted artifacts
    are in their community versions.

    Graylisted artifacts are artifacts that are neither whitelisted nor blacklisted.
    """
    pass

@main.alias_group("check")
def cli_check():
    pass

@main.alias_group("list")
def cli_list():
    pass


@cli_blacklist.command("list")
def blacklist_list():
    """Prints all blacklisted artifacts"""
    blacklist.get_all()

@cli_list.command("black")
def list_black():
    blacklist.get_all()


@cli_blacklist.command("check")
@click.argument('gav', type=da_click.GAV)
def blacklist_check(gav):
    """Checks if artifact is blacklisted. """
    blacklist.get_gav(gav)

@cli_check.command("b")
@click.argument('gav', type=da_click.GAV)
def check_b(gav):
    blacklist.get_gav(gav)
    
@cli_check.command("black")
@click.argument('gav', type=da_click.GAV)
def check_black(gav):
    blacklist.get_gav(gav)
    


if __name__ == '__main__':
    main()

