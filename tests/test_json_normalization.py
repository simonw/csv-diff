from csv_diff import compare, load_json
import io
import json
import pytest


@pytest.mark.parametrize("key", [None, "id"])
def test_missing_and_null_values_compare_equal(key):
    previous = [{"id": 1}, {"id": 2, "name": "Cleo"}]
    current = [{"id": 1, "name": None}, {"id": 2, "name": "Cleo"}]
    result = compare(
        load_json(io.StringIO(json.dumps(previous)), key=key),
        load_json(io.StringIO(json.dumps(current)), key=key),
    )
    assert result == {
        "added": [],
        "removed": [],
        "changed": [],
        "columns_added": [],
        "columns_removed": [],
    }


def test_equivalent_normalized_rows_are_deduplicated_without_key():
    rows = [{"id": 1}, {"id": 1, "name": None}]
    result = load_json(io.StringIO(json.dumps(rows)))
    assert list(result.values()) == [{"id": 1, "name": None}]


def test_missing_explicit_key_is_not_filled_with_null():
    rows = [{"id": 1}, {"name": "Cleo"}]
    with pytest.raises(KeyError):
        load_json(io.StringIO(json.dumps(rows)), key="id")


@pytest.mark.parametrize("value", [{"name": "Cleo"}, ["Cleo", None]])
def test_nested_values_remain_distinct_from_json_strings(value):
    rows = [{"value": value}, {"value": json.dumps(value)}]
    result = load_json(io.StringIO(json.dumps(rows)))
    assert len(result) == 2
    assert list(result.values()) == [{"value": json.dumps(value)}] * 2
