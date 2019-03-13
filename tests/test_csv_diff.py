from csv_diff import load_csv, compare
import io

ONE = """id,name,age
1,Cleo,4
2,Pancakes,2"""

TWO = """id,name,age
1,Cleo,5
2,Pancakes,2"""


def test_diff():
    diff = compare(
        load_csv(io.StringIO(ONE), key="id"), load_csv(io.StringIO(TWO), key="id")
    )
    assert '1 row changed\n\n1 row changed\n\n  Row 1\n    age: "4" => "5"' == diff
