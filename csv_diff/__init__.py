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
            dialect = csv.Sniffer().sniff(peek, delimiters=",\t")
        except csv.Error:
            # Oh well, we tried. Fallback to the default.
            pass
    fp = csv.reader(fp, dialect=(dialect or 'excel'))
    headings = next(fp)
    rows = [dict(zip(headings, line)) for line in fp]
    if key:
        keyfn = lambda r: r[key]
    else:
        keyfn = lambda r: hashlib.sha1(json.dumps(r, sort_keys=True).encode("utf8"))
    return {keyfn(r): r for r in rows}


def compare(previous, current):
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
            d = list(diff(previous[id], current[id], ignore=ignore_columns))
            if d:
                result["changed"].append(
                    {
                        "key": id,
                        "changes": {
                            field: [prev_value, current_value]
                            for _, field, (prev_value, current_value) in d
                        },
                    }
                )
    return result


def human_text(result, key=None, singular=None, plural=None):
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
            rows.append(human_row(row, prefix="  "))
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
            rows.append(human_row(row, prefix="  "))
        summary.append("\n\n".join(rows))
        summary.append("")
    return (", ".join(title) + "\n\n" + ("\n".join(summary))).strip()


def human_row(row, prefix=""):
    bits = []
    for key, value in row.items():
        bits.append("{}{}: {}".format(prefix, key, value))
    return "\n".join(bits)
