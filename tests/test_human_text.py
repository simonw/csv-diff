from csv_diff import load_csv, compare, human_text
from .test_csv_diff import ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN
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


def test_row_changed_show_unchanged():
    diff = compare(
        load_csv(io.StringIO(ONE), key="id"),
        load_csv(io.StringIO(TWO), key="id"),
        show_unchanged=True,
    )
    assert (
        dedent(
            """
    1 row changed

      id: 1
        age: "4" => "5"

        Unchanged:
          name: "Cleo"
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


def test_with_item_nouns():
    "Should have headers for each section here"
    diff = compare(
        load_csv(io.StringIO(ONE), key="id"), load_csv(io.StringIO(SIX), key="id")
    )
    assert (
        dedent(
            """
    1 thing changed, 1 thing added, 1 thing removed

    1 thing changed

      id: 1
        age: "4" => "5"

    1 thing added

      id: 3
      name: Bailey
      age: 1

    1 thing removed

      id: 2
      name: Pancakes
      age: 2
    """
        ).strip()
        == human_text(diff, "id", "thing", "things")
    )


def test_with_plural_nouns():
    diff = compare(
        load_csv(io.StringIO(THREE), key="id"), load_csv(io.StringIO(FIVE), key="id")
    )
    assert (
        dedent(
            """
    3 entities added

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
        == human_text(diff, "id", "entity", "entities")
    )



def test_columns_changed():
    diff = compare(
        load_csv(io.StringIO(SIX), key="id"), load_csv(io.StringIO(SEVEN), key="id")
    )
    assert (
        dedent(
            """
    1 column added, 1 column removed

    1 column added

      weight

    1 column removed

      age
    """
        ).strip()
        == human_text(diff, "id")
    )


def test_columns_and_rows_changed():
    diff = compare(
        load_csv(io.StringIO(SEVEN), key="id"), load_csv(io.StringIO(EIGHT), key="id")
    )
    assert (
        dedent(
            """
    2 columns added, 1 column removed, 1 row changed, 1 row added, 1 row removed

    2 columns added

      age
      length

    1 column removed

      weight

    1 row changed

      id: 3
        name: "Bailey" => "Bailee"

    1 row added

      id: 4
      name: Bob
      age: 7
      length: 422

    1 row removed

      id: 1
      name: Cleo
      weight: 48
    """
        ).strip()
        == human_text(diff, "id")
    )


def test_no_key():
    diff = compare(load_csv(io.StringIO(NINE)), load_csv(io.StringIO(TEN)))
    assert (
        dedent(
            """
        1 row added, 1 row removed

        1 row added

          id: 2
          name: Pancakes
          age: 3

        1 row removed

          id: 2
          name: Pancakes
          age: 4
        """
        ).strip()
        == human_text(diff)
    )
