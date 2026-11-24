from csv_diff import load_csv, compare
import io

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


import io
import pytest


def test_load_csv_row_with_missing_field_raises_clear_error():
    data = "id,name,age\n1,Cleo,4\n2,Pancakes\n"
    with pytest.raises(ValueError) as excinfo:
        load_csv(io.StringIO(data), key="id")
    assert "Line 3: expected 3 fields but found 2" in str(excinfo.value)


def test_load_csv_empty_field_is_allowed():
    data = "id,name,age\n1,Cleo,\n2,Pancakes,2\n"
    rows = load_csv(io.StringIO(data), key="id")
    assert rows["1"] == {"id": "1", "name": "Cleo", "age": ""}


def test_load_csv_quoted_comma_counts_as_one_field():
    data = 'id,name,age\n1,"Cleo, the cat",4\n2,Pancakes,2\n'
    rows = load_csv(io.StringIO(data), key="id")
    assert rows["1"]["name"] == "Cleo, the cat"


def test_load_csv_blank_line_is_skipped():
    data = "id,name,age\n1,Cleo,4\n\n2,Pancakes,2\n"
    rows = load_csv(io.StringIO(data), key="id")
    assert set(rows) == {"1", "2"}


def test_load_csv_extra_fields_keep_existing_behaviour():
    data = "id,name,age\n1,Cleo,4,extra\n2,Pancakes,2\n"
    rows = load_csv(io.StringIO(data), key="id")
    assert rows["1"] == {"id": "1", "name": "Cleo", "age": "4"}