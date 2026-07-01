from csv_diff import load_csv, compare
import io
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


def test_trailing_blank_line_ignored():
    # Issue #29: a trailing newline (as GitHub and most editors emit) should
    # not crash the tool with a KeyError on the key column.
    csv_text = "a,b,c\n1,2,3\n\n"
    assert load_csv(io.StringIO(csv_text), key="a") == {
        "1": {"a": "1", "b": "2", "c": "3"}
    }


def test_interior_blank_line_ignored():
    csv_text = "a,b,c\n1,2,3\n\n4,5,6\n"
    assert load_csv(io.StringIO(csv_text), key="a") == {
        "1": {"a": "1", "b": "2", "c": "3"},
        "4": {"a": "4", "b": "5", "c": "6"},
    }


def test_trailing_blank_line_with_no_key():
    csv_text = "a,b,c\n1,2,3\n\n"
    loaded = load_csv(io.StringIO(csv_text))
    assert list(loaded.values()) == [{"a": "1", "b": "2", "c": "3"}]


def test_mismatched_row_length_raises_clear_error():
    csv_text = "a,b,c\n1,2,3\n4,5\n"
    with pytest.raises(ValueError, match=r"line 3.*2 field.*3"):
        load_csv(io.StringIO(csv_text), key="a")


def test_missing_key_column_raises_clear_error():
    csv_text = "a,b,c\n1,2,3\n"
    with pytest.raises(ValueError, match=r"Key column 'z' not present"):
        load_csv(io.StringIO(csv_text), key="z")
