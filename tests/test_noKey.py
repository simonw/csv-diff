from csv_diff import load_csv, compare, human_text
from .test_csv_diff import NINE, TEN
import io
from textwrap import dedent


def test_no_key():
    diff = compare(
        load_csv(io.StringIO(NINE)), load_csv(io.StringIO(TEN))
    )
    print(diff)
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