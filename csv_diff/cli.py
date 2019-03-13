import click
from . import load_csv, compare


@click.command()
@click.version_option()
@click.argument(
    "previous",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, allow_dash=False),
)
@click.argument(
    "current",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, allow_dash=False),
)
@click.option(
    "--key", type=str, default=None, help="Column to use as a unique ID for each row"
)
def cli(previous, current, key):
    "Diff two CSV files"
    print(compare(load_csv(open(previous), key=key), load_csv(open(current), key=key)))
