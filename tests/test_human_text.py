from csv_diff import load_csv, compare, human_text
from .test_csv_diff import ONE, TWO, THREE, FOUR, FIVE, SIX
from textwrap import dedent
import io


def test_row_changed():
    diff = compare(
        load_csv(io.StringIO(ONE), key="id"), load_csv(io.StringIO(TWO), key="id")
    )
    assert (
        dedent(
            """
    1 row changed

      id: 1
        age: "4" => "5"
    """
        ).strip()
        == human_text(diff, "id")
    )


def test_row_added():
    diff = compare(
        load_csv(io.StringIO(THREE), key="id"), load_csv(io.StringIO(TWO), key="id")
    )
    assert (
        dedent(
            """
    1 row added

      id: 2
      name: Pancakes
      age: 2
    """
        ).strip()
        == human_text(diff, "id")
    )


def test_rows_added():
    diff = compare(
        load_csv(io.StringIO(THREE), key="id"), load_csv(io.StringIO(FIVE), key="id")
    )
    assert (
        dedent(
            """
    3 rows added

      id: 2
      name: Pancakes
      age: 2

      id: 3
      name: Bailey
      age: 1

      id: 4
      name: Carl
      age: 7
    """
        ).strip()
        == human_text(diff, "id")
    )


def test_row_removed():
    diff = compare(
        load_csv(io.StringIO(TWO), key="id"), load_csv(io.StringIO(THREE), key="id")
    )
    assert (
        dedent(
            """
    1 row removed

      id: 2
      name: Pancakes
      age: 2
    """
        ).strip()
        == human_text(diff, "id")
    )


def test_row_changed_and_row_added_and_row_deleted():
    "Should have headers for each section here"
    diff = compare(
        load_csv(io.StringIO(ONE), key="id"), load_csv(io.StringIO(SIX), key="id")
    )
    assert (
        dedent(
            """
    1 row changed, 1 row added, 1 row removed

    1 row changed

      id: 1
        age: "4" => "5"

    1 row added

      id: 3
      name: Bailey
      age: 1

    1 row removed

      id: 2
      name: Pancakes
      age: 2
    """
        ).strip()
        == human_text(diff, "id")
    )
