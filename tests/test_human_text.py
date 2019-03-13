from csv_diff import load_csv, compare, human_text
from .test_csv_diff import ONE, TWO, THREE
import io


def test_row_changed():
    diff = compare(
        load_csv(io.StringIO(ONE), key="id"), load_csv(io.StringIO(TWO), key="id")
    )
    assert (
        '1 row changed\n\n1 row changed\n\n  Row 1\n    age: "4" => "5"'
        == human_text(diff)
    )


def test_row_added():
    diff = compare(
        load_csv(io.StringIO(THREE), key="id"), load_csv(io.StringIO(TWO), key="id")
    )
    assert (
        '1 row added\n\n1 row added\n\n  {"id": "2", "name": "Pancakes", "age": "2"}'
        == human_text(diff)
    )


def test_row_removed():
    diff = compare(
        load_csv(io.StringIO(TWO), key="id"), load_csv(io.StringIO(THREE), key="id")
    )
    assert (
        '1 row removed\n\n1 row removed\n\n  {"id": "2", "name": "Pancakes", "age": "2"}'
        == human_text(diff)
    )
