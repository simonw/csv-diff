# csv-diff

[![PyPI](https://img.shields.io/pypi/v/csv-diff.svg)](https://pypi.org/project/csv-diff/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/csv-diff/blob/master/LICENSE)

Tool for viewing the difference between two CSV files.

Consider two CSV files:

`one.csv`

    id,name,age
    1,Cleo,4
    2,Pancakes,2

`two.csv`

    id,name,age
    1,Cleo,5
    3,Bailey,1

`csv-diff` can show a human-readable summary of differences between the files:

    $ csv-diff one.csv two.csv --key=id
    1 row added, 1 row removed, 1 row changed

    1 row added

      {"id": "3", "name": "Bailey", "age": "1"}

    1 row removed

      {"id": "2", "name": "Pancakes", "age": "2"}

    1 row changed

      Row 1
        age: "4" => "5"

The `--key=id` option means that the `id` column should be treated as the unique key, to identify which records have changed.

You can also run it using the `--json` option to get a machine-readable difference:

    $ csv-diff one.csv two.csv --key=id --json
    {
        "added": [
            {
                "id": "3",
                "name": "Bailey",
                "age": "1"
            }
        ],
        "removed": [
            {
                "id": "2",
                "name": "Pancakes",
                "age": "2"
            }
        ],
        "changed": [
            {
                "key": "1",
                "changes": {
                    "age": [
                        "4",
                        "5"
                    ]
                }
            }
        ]
    }

You can also import the Python library into your own code like so:

    from csv_diff import load_csv, compare
    diff = compare(
        load_csv(open("one.csv"), key="id"),
        load_csv(open("two.csv"), key="id")
    )

`diff` will now contain the same data structure as the output in the `--json` example above.