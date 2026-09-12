from csv_diff import load_csv, load_json, compare
import io
import json
import pytest

ONE = """id,name,age
1,Cleo,4
2,Pancakes,2"""

ONE_TSV = """id\tname\tage
1\tCleo\t4
2\tPancakes\t2"""

TWO = """id,name,age
1,Cleo,5
2,Pancakes,2"""

TWO_TSV = """id\tname\tage
1\tCleo\t5
2\tPancakes\t2"""

THREE = """id,name,age
1,Cleo,5"""

FOUR = """id,name,age
1,Cleo,5
2,Pancakes,2,
3,Bailey,1"""

FIVE = """id,name,age
1,Cleo,5
2,Pancakes,2,
3,Bailey,1
4,Carl,7"""

SIX = """id,name,age
1,Cleo,5
3,Bailey,1"""

SEVEN = """id,name,weight
1,Cleo,48
3,Bailey,20"""

EIGHT = """id,name,age,length
3,Bailee,1,100
4,Bob,7,422"""

NINE = """id,name,age
1,Cleo,5
2,Pancakes,4"""

TEN = """id,name,age
1,Cleo,5
2,Pancakes,3"""


def test_row_changed():
    diff = compare(
        load_csv(io.StringIO(ONE), key="id"), load_csv(io.StringIO(TWO), key="id")
    )
    assert {
        "added": [],
        "removed": [],
        "changed": [{"key": "1", "changes": {"age": ["4", "5"]}}],
        "columns_added": [],
        "columns_removed": [],
    } == diff


def test_row_added():
    diff = compare(
        load_csv(io.StringIO(THREE), key="id"), load_csv(io.StringIO(TWO), key="id")
    )
    assert {
        "changed": [],
        "removed": [],
        "added": [{"age": "2", "id": "2", "name": "Pancakes"}],
        "columns_added": [],
        "columns_removed": [],
    } == diff


def test_row_removed():
    diff = compare(
        load_csv(io.StringIO(TWO), key="id"), load_csv(io.StringIO(THREE), key="id")
    )
    assert {
        "changed": [],
        "removed": [{"age": "2", "id": "2", "name": "Pancakes"}],
        "added": [],
        "columns_added": [],
        "columns_removed": [],
    } == diff


def test_columns_changed():
    diff = compare(
        load_csv(io.StringIO(SIX), key="id"), load_csv(io.StringIO(SEVEN), key="id")
    )
    assert {
        "changed": [],
        "removed": [],
        "added": [],
        "columns_added": ["weight"],
        "columns_removed": ["age"],
    } == diff


def test_tsv():
    diff = compare(
        load_csv(io.StringIO(ONE), key="id"), load_csv(io.StringIO(TWO_TSV), key="id")
    )
    assert {
        "added": [],
        "removed": [],
        "changed": [{"key": "1", "changes": {"age": ["4", "5"]}}],
        "columns_added": [],
        "columns_removed": [],
    } == diff


@pytest.mark.parametrize(
    "content, key_value, duplicate_row",
    [
        ("a,b,c,d\n1,2,3,4\n1,2,3\n3,2,3,4", "1", 2),
        ("a,b\n1,first\n1,last", "1", 2),
        ("a,b\n1,same\n1,same", "1", 2),
        ('a,b\n,"first\ncontinued"\n2,other\n,last', "", 3),
    ],
)
def test_load_csv_rejects_duplicate_explicit_keys(content, key_value, duplicate_row):
    with pytest.raises(ValueError, match="Duplicate key") as error:
        load_csv(io.StringIO(content), key="a")
    message = str(error.value)
    assert repr(key_value) in message
    assert "column 'a'" in message
    assert "data row {}".format(duplicate_row) in message
    assert "first seen at data row 1" in message


@pytest.mark.parametrize("key_value", ["1", 0, None])
def test_load_json_rejects_duplicate_explicit_keys(key_value):
    content = json.dumps(
        [{"id": key_value, "name": "first"}, {"id": key_value, "name": "last"}]
    )
    with pytest.raises(ValueError, match="Duplicate key") as error:
        load_json(io.StringIO(content), key="id")
    message = str(error.value)
    assert repr(key_value) in message
    assert "column 'id'" in message
    assert "data row 2" in message
    assert "first seen at data row 1" in message


@pytest.mark.parametrize(
    "loader, content, expected",
    [
        (load_csv, "id,name\n1,same\n1,same", {"id": "1", "name": "same"}),
        (
            load_json,
            '[{"id": 1, "name": "same"}, {"id": 1, "name": "same"}]',
            {"id": 1, "name": "same"},
        ),
    ],
)
def test_load_without_key_still_deduplicates_identical_rows(loader, content, expected):
    rows = loader(io.StringIO(content))
    assert list(rows.values()) == [expected]
