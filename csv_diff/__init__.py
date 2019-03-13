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
    # Now generate the readable summary
    summary = []
    title = []
    if added:
        fragment = "{} row{} added".format(len(added), "" if len(added) == 1 else "s")
        title.append(fragment)
        summary.append(fragment + "\n")
        for id in added:
            summary.append("  {}".format(json.dumps(current[id])))
        summary.append("")
    if removed:
        fragment = "{} row{} removed".format(
            len(removed), "" if len(removed) == 1 else "s"
        )
        title.append(fragment)
        summary.append(fragment + "\n")
        for id in removed:
            summary.append("  {}".format(json.dumps(previous[id])))
        summary.append("")
    if changed:
        fragment = "{} row{} changed".format(
            len(changed), "" if len(changed) == 1 else "s"
        )
        title.append(fragment)
        summary.append(fragment + "\n")
        for id in changed:
            d = list(diff(previous[id], current[id]))
            summary.append("  Row {}".format(id))
            for _, field, (prev_value, current_value) in d:
                summary.append(
                    '    {}: "{}" => "{}"'.format(field, prev_value, current_value)
                )
            summary.append("")
        summary.append("")
    return (", ".join(title) + "\n\n" + ("\n".join(summary))).strip()
