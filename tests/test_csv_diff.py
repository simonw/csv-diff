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

# Trailing blank line - the most common case (POSIX text files end in \n,
# many editors add an extra one). Used to raise KeyError on the key column.
SEVEN_TRAILING = """id,name,age
1,Cleo,4
2,Pancakes,2
"""

# Multiple trailing blank lines, plus a blank row in the middle of the file.
EIGHT_BLANK = """id,name,age

1,Cleo,4
2,Pancakes,2


"""


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


def test_trailing_blank_line_is_skipped():
    # https://github.com/simonw/csv-diff/issues/29 - a file ending in "\n"
    # (or any number of empty trailing lines) used to produce a dict entry
    # missing every column, which then KeyError'd on the key column. The
    # loader should silently skip blank rows so the rest of the diff runs.
    loaded = load_csv(io.StringIO(SEVEN_TRAILING), key="id")
    assert loaded == {
        "1": {"id": "1", "name": "Cleo", "age": "4"},
        "2": {"id": "2", "name": "Pancakes", "age": "2"},
    }


def test_multiple_blank_lines_and_interior_blank_skipped():
    # A blank row in the middle and several trailing blank lines should all
    # be dropped - the loader treats csv.reader's empty `line` as the marker
    # of a row that contributed no fields.
    loaded = load_csv(io.StringIO(EIGHT_BLANK), key="id")
    assert loaded == {
        "1": {"id": "1", "name": "Cleo", "age": "4"},
        "2": {"id": "2", "name": "Pancakes", "age": "2"},
    }


def test_compare_with_trailing_blank_lines():
    # End-to-end: comparing two identical files where both have a trailing
    # newline should report no changes (regression check for issue #29).
    a = "id,name,age\n1,Cleo,4\n"
    b = "id,name,age\n1,Cleo,4\n"
    diff = compare(load_csv(io.StringIO(a), key="id"), load_csv(io.StringIO(b), key="id"))
    assert diff == {
        "added": [],
        "removed": [],
        "changed": [],
        "columns_added": [],
        "columns_removed": [],
    }
