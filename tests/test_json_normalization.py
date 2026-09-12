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


def test_unrelated_column_changes_do_not_replace_identical_rows():
    result = compare(
        load_json(io.StringIO('[{"id": 1}, {"a": 0}]')),
        load_json(io.StringIO('[{"id": 1}, {"b": 0}]')),
    )
    assert result == {
        "added": [{"b": 0, "id": None}],
        "removed": [{"a": 0, "id": None}],
        "changed": [],
        "columns_added": ["b"],
        "columns_removed": ["a"],
    }


@pytest.mark.parametrize("value", [None, 0, False, "", [], {}])
def test_new_column_preserves_non_null_row_differences(value):
    previous = [{"id": 1}]
    current = [{"id": 1, "extra": value}]
    result = compare(
        load_json(io.StringIO(json.dumps(previous))),
        load_json(io.StringIO(json.dumps(current))),
    )
    displayed = json.dumps(value) if isinstance(value, (list, dict)) else value
    assert result == {
        "added": [] if value is None else [{"id": 1, "extra": displayed}],
        "removed": [] if value is None else previous,
        "changed": [],
        "columns_added": ["extra"],
        "columns_removed": [],
    }


def test_nested_null_fields_are_not_ignored():
    result = compare(
        load_json(io.StringIO('[{"value": {}}]')),
        load_json(io.StringIO('[{"value": {"field": null}}]')),
    )
    assert result == {
        "added": [{"value": '{"field": null}'}],
        "removed": [{"value": "{}"}],
        "changed": [],
        "columns_added": [],
        "columns_removed": [],
    }


def test_explicit_key_still_uses_last_duplicate_row():
    rows = [{"id": 1, "value": "old"}, {"id": 1, "value": None}]
    assert load_json(io.StringIO(json.dumps(rows)), key="id") == {
        1: {"id": 1, "value": None}
    }


def test_empty_key_argument_still_uses_content_keys():
    source = '[{"": "same", "value": 0}, {"": "same", "value": false}]'
    result = load_json(io.StringIO(source), key="")
    assert result == load_json(io.StringIO(source))
    assert len(result) == 2
    assert "same" not in result
