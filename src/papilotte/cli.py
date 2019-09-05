"""Command line command for papilotte.
"""
import logging
import click
from clickclick import AliasedGroup
from papilotte import __version__, create_app

logger = logging.getLogger('papilotte.cli')


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def print_version(ctx, param, value):
    "Print papilotte version."
    if not value or ctx.resilient_parsing:
        return
    click.echo('Papilotte {}'.format(__version__))
    ctx.exit()


@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
@click.option('-V', '--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True,
              help='Show the current version and exit')
def main():
    "Empty function for param --version."


# DO NOT DEFINE DEFAULT VALUES OR OVERRIDING CONFIGURATION VALUES
# WILL BREAK! CHANGE VALUES IN config/default_config.yml INSTEAD!
@main.command()
@click.option('--spec-file', '-s', type=click.Path(),
              help=('Path to the openapi spec file. '
                    'Use only if you need a customized spec file.'))
@click.option('--config-file', '-c', type=click.Path(),
              help=('Path to the configuration file. '
                    'Values defined there are overriden by values '
                    'from command line arguments.'))
@click.option('--port', '-p', type=int, help='Port to listen.')
@click.option('--host', '-h', help='Host interface to bind to.')
@click.option('--debug', '-d', type=click.BOOL, is_flag=True,
              default=False, help='Run in debug mode')
@click.option('--compliance-level', type=click.Choice(('0', '1', '2')),
              help=('Set the compliance level to 0 (TODO), 1 (TODO) '
                    'or 2 (TODO)'))
@click.option('--connector', '-n',
              help='The connector module or package to use')
@click.option('--base-path', metavar="PATH",
              help="Override the basePath in the API spec")
def run(**params):
    """Run the Papilotte server.

    Run papilotte run --help to see paramaters.
    """
    app = create_app(**params)
    app.run()


if __name__ == '__main__':
    main()
