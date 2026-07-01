import csv
from dictdiffer import diff
import json
import hashlib


def load_csv(fp, key=None, dialect=None):
    if dialect is None and fp.seekable():
        # Peek at first 1MB to sniff the delimiter and other dialect details
        peek = fp.read(1024**2)
        fp.seek(0)
        try:
            dialect = csv.Sniffer().sniff(peek, delimiters=",\t;")
        except csv.Error:
            # Oh well, we tried. Fallback to the default.
            pass
    fp = csv.reader(fp, dialect=(dialect or "excel"))
    try:
        headings = next(fp)
    except StopIteration:
        raise ValueError("CSV input is empty (no header row found)")
    if not headings:
        raise ValueError("CSV input has an empty header row")
    rows = {}
    # Track the 1-based source line number alongside each row so that any
    # downstream KeyError or value-shape error can point back to the line
    # in the input file the user just gave us. The header is on line 1.
    for line_number, line in enumerate(fp, start=2):
        # csv.reader yields an empty list for a fully-blank line (a stray
        # trailing newline, the kind GitHub and most editors insert by
        # default). Silently skipping those matches the "POSIX text file"
        # convention and the behaviour of most other CSV tools; raising
        # KeyError('a') at the very end of a diff made the tool look
        # broken on perfectly normal input. See issue #29.
        if not line:
            continue
        if len(line) < len(headings):
            raise ValueError(
                f"CSV row on line {line_number} has {len(line)} field(s) "
                f"but the header on line 1 has {len(headings)}; "
                f"got {line!r}"
            )
        rows[line_number] = dict(zip(headings, line))
    if key:
        try:
            return {rows[ln][key]: rows[ln] for ln in rows}
        except KeyError as exc:
            missing = exc.args[0]
            raise ValueError(
                f"Key column {missing!r} not present in CSV header "
                f"{headings!r}"
            ) from None
    else:
        return {
            hashlib.sha1(
                json.dumps(rows[ln], sort_keys=True).encode("utf8")
            ).hexdigest(): rows[ln]
            for ln in rows
        }


def load_json(fp, key=None):
    raw_list = json.load(fp)
    assert isinstance(raw_list, list)
    common_keys = set()
    for item in raw_list:
        common_keys.update(item.keys())
    if key:
        keyfn = lambda r: r[key]
    else:
        keyfn = lambda r: hashlib.sha1(
            json.dumps(r, sort_keys=True).encode("utf8")
        ).hexdigest()
    return {keyfn(r): _simplify_json_row(r, common_keys) for r in raw_list}


def _simplify_json_row(r, common_keys):
    # Convert list/dict values into JSON serialized strings
    for key, value in r.items():
        if isinstance(value, (dict, tuple, list)):
            r[key] = json.dumps(value)
    for key in common_keys:
        if key not in r:
            r[key] = None
    return r


def compare(previous, current, show_unchanged=False):
    result = {
        "added": [],
        "removed": [],
        "changed": [],
        "columns_added": [],
        "columns_removed": [],
    }
    # Have the columns changed?
    previous_columns = set(next(iter(previous.values())).keys())
    current_columns = set(next(iter(current.values())).keys())
    ignore_columns = None
    if previous_columns != current_columns:
        result["columns_added"] = [
            c for c in current_columns if c not in previous_columns
        ]
        result["columns_removed"] = [
            c for c in previous_columns if c not in current_columns
        ]
        ignore_columns = current_columns.symmetric_difference(previous_columns)
    # Have any rows been removed or added?
    removed = [id for id in previous if id not in current]
    added = [id for id in current if id not in previous]
    # How about changed?
    removed_or_added = set(removed) | set(added)
    potential_changes = [id for id in current if id not in removed_or_added]
    changed = [id for id in potential_changes if current[id] != previous[id]]
    if added:
        result["added"] = [current[id] for id in added]
    if removed:
        result["removed"] = [previous[id] for id in removed]
    if changed:
        for id in changed:
            diffs = list(diff(previous[id], current[id], ignore=ignore_columns))
            if diffs:
                changes = {
                    "key": id,
                    "changes": {
                        # field can be a list if id contained '.' - #7
                        field[0] if isinstance(field, list) else field: [
                            prev_value,
                            current_value,
                        ]
                        for _, field, (prev_value, current_value) in diffs
                    },
                }
                if show_unchanged:
                    changes["unchanged"] = {
                        field: value
                        for field, value in previous[id].items()
                        if field not in changes["changes"] and field != "id"
                    }
                result["changed"].append(changes)
    return result


def human_text(result, key=None, singular=None, plural=None, current=None, extras=None):
    singular = singular or "row"
    plural = plural or "rows"
    title = []
    summary = []
    show_headers = sum(1 for key in result if result[key]) > 1
    if result["columns_added"]:
        fragment = "{} {} added".format(
            len(result["columns_added"]),
            "column" if len(result["columns_added"]) == 1 else "columns",
        )
        title.append(fragment)
        summary.extend(
            [fragment, ""]
            + ["  {}".format(c) for c in sorted(result["columns_added"])]
            + [""]
        )
    if result["columns_removed"]:
        fragment = "{} {} removed".format(
            len(result["columns_removed"]),
            "column" if len(result["columns_removed"]) == 1 else "columns",
        )
        title.append(fragment)
        summary.extend(
            [fragment, ""]
            + ["  {}".format(c) for c in sorted(result["columns_removed"])]
            + [""]
        )
    if result["changed"]:
        fragment = "{} {} changed".format(
            len(result["changed"]), singular if len(result["changed"]) == 1 else plural
        )
        title.append(fragment)
        if show_headers:
            summary.append(fragment + "\n")
        change_blocks = []
        for details in result["changed"]:
            block = []
            block.append("  {}: {}".format(key, details["key"]))
            for field, (prev_value, current_value) in details["changes"].items():
                block.append(
                    '    {}: "{}" => "{}"'.format(field, prev_value, current_value)
                )
            if extras:
                current_item = current[details["key"]]
                block.append(human_extras(current_item, extras))
            block.append("")
            change_blocks.append("\n".join(block))
            if details.get("unchanged"):
                block = []
                block.append("    Unchanged:")
                for field, value in details["unchanged"].items():
                    block.append('      {}: "{}"'.format(field, value))
                block.append("")
                change_blocks.append("\n".join(block))
        summary.append("\n".join(change_blocks))
    if result["added"]:
        fragment = "{} {} added".format(
            len(result["added"]), singular if len(result["added"]) == 1 else plural
        )
        title.append(fragment)
        if show_headers:
            summary.append(fragment + "\n")
        rows = []
        for row in result["added"]:
            to_append = human_row(row, prefix="  ")
            if extras:
                to_append += "\n" + human_extras(row, extras)
            rows.append(to_append)
        summary.append("\n\n".join(rows))
        summary.append("")
    if result["removed"]:
        fragment = "{} {} removed".format(
            len(result["removed"]), singular if len(result["removed"]) == 1 else plural
        )
        title.append(fragment)
        if show_headers:
            summary.append(fragment + "\n")
        rows = []
        for row in result["removed"]:
            to_append = human_row(row, prefix="  ")
            if extras:
                to_append += "\n" + human_extras(row, extras)
            rows.append(to_append)
        summary.append("\n\n".join(rows))
        summary.append("")
    return (", ".join(title) + "\n\n" + ("\n".join(summary))).strip()


def human_row(row, prefix=""):
    bits = []
    for key, value in row.items():
        bits.append("{}{}: {}".format(prefix, key, value))
    return "\n".join(bits)


def human_extras(row, extras):
    bits = []
    bits.append("  extras:")
    for key, fmt in extras:
        bits.append("    {}: {}".format(key, fmt.format(**row)))
    return "\n".join(bits)
