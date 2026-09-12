from click.testing import CliRunner
from csv_diff import cli, load_csv
import csv
import pytest
from .test_csv_diff import ONE, ONE_TSV, TWO, TWO_TSV, THREE, FIVE
import io
import json
from textwrap import dedent


@pytest.fixture
def tsv_files(tmpdir):
    one = tmpdir / "one.tsv"
    one.write(ONE_TSV)
    two = tmpdir / "two.tsv"
    two.write(TWO_TSV)
    return str(one), str(two)


@pytest.fixture
def json_files(tmpdir):
    one = tmpdir / "one.json"
    one.write(
        json.dumps(
            [
                {"id": 1, "name": "Cleo", "nested": {"foo": 3}, "extra": 1},
                {"id": 2, "name": "Pancakes", "nested": {"foo": 3}},
            ]
        )
    )
    two = tmpdir / "two.json"
    two.write(
        json.dumps(
            [
                {"id": 1, "name": "Cleo", "nested": {"foo": 3, "bar": 5}, "extra": 1},
                {"id": 2, "name": "Pancakes!", "nested": {"foo": 3}, "extra": 1},
            ]
        )
    )
    return str(one), str(two)


def test_human_cli(tmpdir):
    one = tmpdir / "one.csv"
    one.write(ONE)
    two = tmpdir / "two.csv"
    two.write(TWO)
    result = CliRunner().invoke(cli.cli, [str(one), str(two), "--key", "id"])
    assert 0 == result.exit_code
    assert (
        dedent(
            """
    1 row changed

      id: 1
        age: "4" => "5"
    """
        ).strip()
        == result.output.strip()
    )


def test_human_cli_alternative_names(tmpdir):
    one = tmpdir / "one.csv"
    one.write(ONE)
    five = tmpdir / "five.csv"
    five.write(FIVE)
    result = CliRunner().invoke(
        cli.cli,
        [str(one), str(five), "--key", "id", "--singular", "tree", "--plural", "trees"],
    )
    assert 0 == result.exit_code, result.output
    assert (
        dedent(
            """
    1 tree changed, 2 trees added

    1 tree changed

      id: 1
        age: "4" => "5"

    2 trees added

      id: 3
      name: Bailey
      age: 1

      id: 4
      name: Carl
      age: 7
    """
        ).strip()
        == result.output.strip()
    )


def test_human_cli_json(tmpdir):
    one = tmpdir / "one.csv"
    one.write(ONE)
    two = tmpdir / "two.csv"
    two.write(TWO)
    result = CliRunner().invoke(cli.cli, [str(one), str(two), "--key", "id", "--json"])
    assert 0 == result.exit_code
    assert {
        "added": [],
        "removed": [],
        "changed": [{"key": "1", "changes": {"age": ["4", "5"]}}],
        "columns_added": [],
        "columns_removed": [],
    } == json.loads(result.output.strip())


def test_tsv_files(tsv_files):
    one, two = tsv_files
    result = CliRunner().invoke(
        cli.cli, [one, two, "--key", "id", "--json", "--format", "tsv"]
    )
    assert 0 == result.exit_code
    assert {
        "added": [],
        "removed": [],
        "changed": [{"key": "1", "changes": {"age": ["4", "5"]}}],
        "columns_added": [],
        "columns_removed": [],
    } == json.loads(result.output.strip())


def test_json_files(json_files):
    one, two = json_files
    result = CliRunner().invoke(
        cli.cli,
        [one, two, "--key", "id", "--json", "--format", "json"],
        catch_exceptions=False,
    )
    assert 0 == result.exit_code
    assert {
        "added": [],
        "removed": [],
        "changed": [
            {"key": 1, "changes": {"nested": ['{"foo": 3}', '{"foo": 3, "bar": 5}']}},
            {
                "key": 2,
                "changes": {"name": ["Pancakes", "Pancakes!"], "extra": [None, 1]},
            },
        ],
        "columns_added": [],
        "columns_removed": [],
    } == json.loads(result.output.strip())


def test_sniff_format(tsv_files):
    one, two = tsv_files
    result = CliRunner().invoke(cli.cli, [one, two, "--key", "id", "--json"])
    assert 0 == result.exit_code
    assert {
        "added": [],
        "removed": [],
        "changed": [{"key": "1", "changes": {"age": ["4", "5"]}}],
        "columns_added": [],
        "columns_removed": [],
    } == json.loads(result.output.strip())


def test_format_overrides_sniff(tsv_files):
    one, two = tsv_files
    result = CliRunner().invoke(
        cli.cli, [one, two, "--key", "id", "--json", "--format", "csv"]
    )
    assert 1 == result.exit_code


def test_column_containing_dot(tmpdir):
    # https://github.com/simonw/csv-diff/issues/7
    one = tmpdir / "one.csv"
    two = tmpdir / "two.csv"
    one.write(
        dedent(
            """
    id,foo.bar,foo.baz
    1,Dog,Cat
    """
        ).strip()
    )
    two.write(
        dedent(
            """
    id,foo.bar,foo.baz
    1,Dog,Beaver
    """
        ).strip()
    )
    result = CliRunner().invoke(
        cli.cli, [str(one), str(two), "--key", "id", "--json"], catch_exceptions=False
    )
    assert 0 == result.exit_code
    assert {
        "added": [],
        "removed": [],
        "changed": [{"key": "1", "changes": {"foo.baz": ["Cat", "Beaver"]}}],
        "columns_added": [],
        "columns_removed": [],
    } == json.loads(result.output.strip())


def test_semicolon_delimited(tmpdir):
    # https://github.com/simonw/csv-diff/issues/6
    one = tmpdir / "one.csv"
    two = tmpdir / "two.csv"
    one.write(
        dedent(
            """
    id;name
    1;Mark
    """
        ).strip()
    )
    two.write(
        dedent(
            """
    id;name
    1;Brian
    """
        ).strip()
    )
    result = CliRunner().invoke(
        cli.cli, [str(one), str(two), "--key", "id", "--json"], catch_exceptions=False
    )
    assert 0 == result.exit_code
    assert {
        "added": [],
        "removed": [],
        "changed": [{"key": "1", "changes": {"name": ["Mark", "Brian"]}}],
        "columns_added": [],
        "columns_removed": [],
    } == json.loads(result.output.strip())


def test_diff_with_extras(tmpdir):
    one = tmpdir / "one.json"
    two = tmpdir / "two.json"
    one.write(
        json.dumps(
            [
                {"id": 1, "name": "Cleo", "type": "dog"},
                {"id": 2, "name": "Suna", "type": "chicken"},
            ]
        )
    )
    two.write(
        json.dumps(
            [
                {"id": 2, "name": "Suna", "type": "pretty chicken"},
                {"id": 3, "name": "Artie", "type": "bunny"},
            ]
        )
    )
    result = CliRunner().invoke(
        cli.cli,
        [
            str(one),
            str(two),
            "--key",
            "id",
            "--format",
            "json",
            "--extra",
            "search",
            "https://www.google.com/search?q={name}",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    expected = dedent(
        """
    1 row changed, 1 row added, 1 row removed

    1 row changed

      id: 2
        type: "chicken" => "pretty chicken"
      extras:
        search: https://www.google.com/search?q=Suna

    1 row added

      id: 3
      name: Artie
      type: bunny
      extras:
        search: https://www.google.com/search?q=Artie

    1 row removed

      id: 1
      name: Cleo
      type: dog
      extras:
        search: https://www.google.com/search?q=Cleo
    """
    ).strip()
    assert result.output.strip() == expected


@pytest.mark.parametrize("format", ["csv", "tsv", "json"])
@pytest.mark.parametrize("duplicate_in", ["previous", "current"])
@pytest.mark.parametrize("key_name", ["id", ""])
def test_cli_reports_duplicate_key_with_input_filename(
    tmpdir, format, duplicate_in, key_name
):
    paths = []
    for side in ("previous", "current"):
        path = tmpdir / "{}.{}".format(side, format)
        if format == "json":
            rows = [{key_name: 1, "name": "first"}]
            if side == duplicate_in:
                rows.append({key_name: 1, "name": "last"})
            content = json.dumps(rows)
        else:
            delimiter = "\t" if format == "tsv" else ","
            content = "{1}{0}name\n1{0}first\n".format(delimiter, key_name)
            if side == duplicate_in:
                content += "1{}last\n".format(delimiter)
        path.write(content)
        paths.append(str(path))
    result = CliRunner().invoke(
        cli.cli,
        paths + ["--key", key_name, "--format", format, "--json"],
        catch_exceptions=False,
    )
    assert result.exit_code == 1
    assert result.output.startswith("Error:")
    assert "{}.{}".format(duplicate_in, format) in result.output
    assert "Duplicate key" in result.output
    assert "column {!r}".format(key_name) in result.output
    assert "data row 2" in result.output
    assert "first seen at data row 1" in result.output
