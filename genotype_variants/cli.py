# -*- coding: utf-8 -*-
import os
import sys
import pathlib
import logging
try:
    import click
except ImportError as e:
    print(
        "cli: click is not installed, please install click as it is one of the requirements."
    )
    exit(1)
try:
    import click_log
except ImportError as e:
    print(
        "cli: click-log is not installed, please install click_log as it is one of the requirements."
    )
    exit(1)

"""
cli
~~~~~~~~~~~~~~~
:Description: console script for running genotyping
"""
"""
Created on January 29, 2020
Description: console script for running genotyping
@author: Ronak H Shah
"""

version = None
scriptpath = os.path.realpath(__file__)
p_scriptpath = pathlib.Path(scriptpath)
with open(os.path.join(p_scriptpath.parent, "__init__.py"), "r") as f:
    for line in f.readlines():
        line = line.strip()
        if line.startswith("__version__"):
            version = line.split("=")[-1].strip()
__all__ = []
__version__ = version
__date__ = "2020-01-29"
__updated__ = "2022-04-28"

plugin_folder = os.path.join(os.path.dirname(__file__), 'commands')

class MyCLI(click.MultiCommand):

    def list_commands(self, ctx):
        """Dynamically get the list of commands."""
        rv = []
        for filename in os.listdir(plugin_folder):
            if filename.endswith('.py') and not filename.startswith('__init__'):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        """Dynamically get the command."""
        ns = {}
        fn = os.path.join(plugin_folder, name + '.py')
        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            eval(code, ns, ns)
        return ns['cli']


@click.command(cls=MyCLI)
@click.version_option(None, "-v", "--version", message="%(version)s", prog_name="genotype_variants")
def main(args=None):
    """Console script for genotype_variants."""
    pass


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
