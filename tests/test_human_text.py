from csv_diff import load_csv, compare, human_text
from .test_csv_diff import ONE, TWO, THREE, FOUR
import io


def test_row_changed():
    diff = compare(
        load_csv(io.StringIO(ONE), key="id"), load_csv(io.StringIO(TWO), key="id")
    )
    assert '1 row changed\n\n  Row 1\n    age: "4" => "5"' == human_text(diff)


def test_row_added():
    diff = compare(
        load_csv(io.StringIO(THREE), key="id"), load_csv(io.StringIO(TWO), key="id")
    )
    assert '1 row added\n\n  {"id": "2", "name": "Pancakes", "age": "2"}' == human_text(
        diff
    )


def test_row_removed():
    diff = compare(
        load_csv(io.StringIO(TWO), key="id"), load_csv(io.StringIO(THREE), key="id")
    )
    assert (
        '1 row removed\n\n  {"id": "2", "name": "Pancakes", "age": "2"}'
        == human_text(diff)
    )


def test_row_changed_and_row_added():
    "Should have headers for each section here"
    diff = compare(
        load_csv(io.StringIO(ONE), key="id"), load_csv(io.StringIO(FOUR), key="id")
    )
    assert (
        "1 row changed, 1 row added\n\n"
        "1 row changed\n\n"
        "  Row 1\n"
        '    age: "4" => "5"\n\n'
        "1 row added\n\n"
        '  {"id": "3", "name": "Bailey", "age": "1"}'
    ) == human_text(diff)
