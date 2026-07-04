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


def test_load_csv_handles_fields_larger_than_default_limit():
    # Regression test for https://github.com/simonw/csv-diff/issues/41
    # The csv module's default per-field size cap is 131072 bytes; rows with
    # longer fields (e.g. nucleotide sequences, large JSON blobs) used to
    # raise ``_csv.Error: field larger than field limit (131072)`` from
    # ``load_csv``. ``load_csv`` now bumps the cap to ``sys.maxsize`` so
    # these rows are returned in full.
    long_value = "A" * (200_000)
    csv_text = f"id,sequence\n1,{long_value}\n"
    rows = load_csv(io.StringIO(csv_text), key="id")
    assert rows == {"1": {"id": "1", "sequence": long_value}}


def test_load_csv_handles_tsv_with_long_fields():
    # Same fix as above, exercising the TSV path (which uses the same
    # underlying csv reader and is also subject to the size cap).
    long_value = "T" * (200_000)
    tsv_text = f"id\tsequence\n1\t{long_value}\n"
    rows = load_csv(io.StringIO(tsv_text), key="id")
    assert rows == {"1": {"id": "1", "sequence": long_value}}


def test_compare_handles_double_dot_in_column_name():
    # Regression test for https://github.com/simonw/csv-diff/issues/40
    # dictdiffer's default ``dot_notation=True`` parses ``..`` in a key as a
    # parent step in a path, which causes a ``ValueError: not enough values
    # to unpack (expected 2, got 1)`` when one row's value sits at a top-
    # level key like ``name..date_range``. compare() now passes
    # ``dot_notation=False`` so dictdiffer treats every column name as a
    # flat string and the unpack always sees the expected 3-tuple shape.
    previous = load_csv(io.StringIO(ONE_DOTDOT), key="id")
    current = load_csv(io.StringIO(TWO_DOTDOT), key="id")
    diff = compare(previous, current)
    # The ``..`` column is reported as a column-level change (added in
    # current, removed from previous) and the timestamp value change
    # surfaces in the per-row change block.
    assert diff["columns_added"] == ["name..date_range"]
    assert diff["columns_removed"] == ["name.date_range"]
    assert diff["changed"] == [
        {"key": "1", "changes": {"timestamp": ["1", "2"]}}
    ]
    assert diff["added"] == []
    assert diff["removed"] == []


def test_compare_handles_double_dot_in_column_value_change():
    # Same fix as above, exercising the case where the column with ``..`` is
    # present in both rows and only its value changes. Without
    # ``dot_notation=False`` dictdiffer returns the path as
    # ``['name..date_range']`` (a list with the double-dot in it) and the
    # existing code's ``field[0]`` flattening still produces the right
    # field name in the changes block.
    previous = load_csv(io.StringIO(DOTDOT_VAL_OLD), key="id")
    current = load_csv(io.StringIO(DOTDOT_VAL_NEW), key="id")
    diff = compare(previous, current)
    assert diff["columns_added"] == []
    assert diff["columns_removed"] == []
    assert diff["changed"] == [
        {"key": "1", "changes": {"name..date_range": ["A", "B"]}}
    ]


ONE_DOTDOT = """id,name.date_range,timestamp
1,X,1
"""
TWO_DOTDOT = """id,name..date_range,timestamp
1,X,2
"""

DOTDOT_VAL_OLD = """id,name..date_range
1,A
"""
DOTDOT_VAL_NEW = """id,name..date_range
1,B
"""