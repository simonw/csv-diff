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


def test_human_cli_non_utf8_encoding(tmpdir):
    # This test confirms the ability to parse csv files that are not encoded using utf-8.
    # The names in the files contain characters that would cause UnicodeDecodeErrors if they
    # are encoeded using cp1252 and then parsed using utf-8.
    encoding = "cp1252"
    one = tmpdir / "one.csv"
    two = tmpdir / "two.csv"
    one.write_binary(
        dedent(
            """
    id;name
    1;José
    """
        ).strip().encode(encoding)
    )
    two.write_binary(
        dedent(
            """
    id;name
    1;Ángela
    """
        ).strip().encode(encoding)
    )
    result = CliRunner().invoke(
        cli.cli, [str(one), str(two), "--key", "id", "--encoding", encoding], catch_exceptions=False
    )
    assert 0 == result.exit_code
    assert (
        dedent(
            """
    1 row changed

      id: 1
        name: "José" => "Ángela"
    """
        ).strip()
        == result.output.strip()
    )
