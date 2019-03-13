import csv
from dictdiffer import diff
import json
import hashlib


def load_csv(fp, key=None):
    fp = csv.reader(fp)
    headings = next(fp)
    rows = [dict(zip(headings, line)) for line in fp]
    if key:
        keyfn = lambda r: r[key]
    else:
        keyfn = lambda r: hashlib.sha1(json.dumps(r, sort_keys=True).encode("utf8"))
    return {keyfn(r): r for r in rows}


def compare(previous, current):
    # Have any rows been removed or added?
    removed = [id for id in previous if id not in current]
    added = [id for id in current if id not in previous]
    # How about changed?
    removed_or_added = set(removed) | set(added)
    potential_changes = [id for id in current if id not in removed_or_added]
    changed = [id for id in potential_changes if current[id] != previous[id]]
    result = {"added": [], "removed": [], "changed": []}
    if added:
        result["added"] = [current[id] for id in added]
    if removed:
        result["removed"] = [previous[id] for id in removed]
    if changed:
        for id in changed:
            d = list(diff(previous[id], current[id]))
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


def human_text(result):
    title = []
    summary = []
    show_headers = sum(1 for key in result if result[key]) > 1
    if result["changed"]:
        fragment = "{} row{} changed".format(
            len(result["changed"]), "" if len(result["changed"]) == 1 else "s"
        )
        title.append(fragment)
        if show_headers:
            summary.append(fragment + "\n")
        change_blocks = []
        for details in result["changed"]:
            block = []
            block.append("  Row {}".format(details["key"]))
            for field, (prev_value, current_value) in details["changes"].items():
                block.append(
                    '    {}: "{}" => "{}"'.format(field, prev_value, current_value)
                )
            block.append("")
            change_blocks.append("\n".join(block))
        summary.append("\n".join(change_blocks))
    if result["added"]:
        fragment = "{} row{} added".format(
            len(result["added"]), "" if len(result["added"]) == 1 else "s"
        )
        title.append(fragment)
        if show_headers:
            summary.append(fragment + "\n")
        for row in result["added"]:
            summary.append("  {}".format(json.dumps(row)))
        summary.append("")
    if result["removed"]:
        fragment = "{} row{} removed".format(
            len(result["removed"]), "" if len(result["removed"]) == 1 else "s"
        )
        title.append(fragment)
        if show_headers:
            summary.append(fragment + "\n")
        for row in result["removed"]:
            summary.append("  {}".format(json.dumps(row)))
        summary.append("")
    return (", ".join(title) + "\n\n" + ("\n".join(summary))).strip()
