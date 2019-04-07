import click
import json as std_json
from . import load_csv, compare, human_text


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
@click.option(
    "--json", type=bool, default=False, help="Output changes as JSON", is_flag=True
)
def cli(previous, current, key, json):
    "Diff two CSV files"
    diff = compare(load_csv(open(previous), key=key), load_csv(open(current), key=key))
    if json:
        print(std_json.dumps(diff, indent=4))
    else:
        print(human_text(diff, key))
