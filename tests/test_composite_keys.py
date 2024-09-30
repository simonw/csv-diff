from csv_diff import load_csv, compare
import io

# Multi-key Tests

# Base CSV: MULTI_KEY_BASE
MULTI_KEY_BASE = """Customer ID,Timestamp,Product Name,Quantity
CUST-001,2022-01-01 10:00:00,Chair,2
CUST-001,2022-01-02 11:00:00,Table,1
CUST-002,2022-01-02 11:00:00,Desk,3"""

# Modified CSV: MULTI_KEY_ROW_CHANGED
MULTI_KEY_ROW_CHANGED = """Customer ID,Timestamp,Product Name,Quantity
CUST-001,2022-01-01 10:00:00,Chair,3
CUST-001,2022-01-02 11:00:00,Table,1
CUST-002,2022-01-02 11:00:00,Desk,3"""

# Modified CSV: MULTI_KEY_ROW_ADDED
MULTI_KEY_ROW_ADDED = """Customer ID,Timestamp,Product Name,Quantity
CUST-001,2022-01-01 10:00:00,Chair,2
CUST-001,2022-01-02 11:00:00,Table,1
CUST-002,2022-01-02 11:00:00,Desk,3
CUST-003,2022-01-03 12:00:00,Bookshelf,1"""

# Modified CSV: MULTI_KEY_ROW_REMOVED
MULTI_KEY_ROW_REMOVED = """Customer ID,Timestamp,Product Name,Quantity
CUST-001,2022-01-01 10:00:00,Chair,2
CUST-002,2022-01-02 11:00:00,Desk,3"""

# Modified CSV: MULTI_KEY_ROW_REMOVED_AND_CHANGE
MULTI_KEY_ROW_REMOVED_AND_CHANGE = """Customer ID,Timestamp,Product Name,Quantity
CUST-001,2022-01-01 10:00:00,Chair,3
CUST-002,2022-01-02 11:00:00,Desk,3"""

# Modified CSV: MULTI_KEY_COLUMN_ADD
MULTI_KEY_COLUMN_ADD = """Customer ID,Timestamp,Product Name,Price
CUST-001,2022-01-01 10:00:00,Chair,19.99
CUST-001,2022-01-02 11:00:00,Table,49.99
CUST-002,2022-01-02 11:00:00,Desk,99.99"""

# Modified CSV: MULTI_KEY_PRIMARY_KEY_CHANGED
MULTI_KEY_PRIMARY_KEY_CHANGED = """Customer ID,Timestamp,Product Name,Quantity
CUST-001,2022-01-01 10:00:00,Chair,2
CUST-003,2022-01-02 11:00:00,Table,1
CUST-002,2022-01-02 11:00:00,Desk,3"""

# Multi-Key Tests

multi_key = ("Customer ID", "Timestamp")

def test_multi_key_row_changed():
    diff = compare(
        load_csv(io.StringIO(MULTI_KEY_BASE), key=multi_key),
        load_csv(io.StringIO(MULTI_KEY_ROW_CHANGED), key=multi_key)
    )
    assert {
        "added": [],
        "removed": [],
        "changed": [
            {
                "key": ("CUST-001", "2022-01-01 10:00:00"),
                "changes": {"Quantity": ["2", "3"]}
            }
        ],
        "columns_added": [],
        "columns_removed": [],
    } == diff


def test_multi_key_row_added():
    diff = compare(
        load_csv(io.StringIO(MULTI_KEY_BASE), key=multi_key),
        load_csv(io.StringIO(MULTI_KEY_ROW_ADDED), key=multi_key)
    )
    assert {
        "changed": [],
        "removed": [],
        "added": [
            {"Customer ID": "CUST-003", "Timestamp": "2022-01-03 12:00:00", "Product Name": "Bookshelf", "Quantity": "1"}
        ],
        "columns_added": [],
        "columns_removed": [],
    } == diff


def test_multi_key_row_removed():
    diff = compare(
        load_csv(io.StringIO(MULTI_KEY_BASE), key=multi_key),
        load_csv(io.StringIO(MULTI_KEY_ROW_REMOVED), key=multi_key)
    )
    assert {
        "changed": [],
        "removed": [
            {"Customer ID": "CUST-001", "Timestamp": "2022-01-02 11:00:00", "Product Name": "Table", "Quantity": "1"}
        ],
        "added": [],
        "columns_added": [],
        "columns_removed": [],
    } == diff

def test_multi_key_row_removed_and_change():
    diff = compare(
        load_csv(io.StringIO(MULTI_KEY_BASE), key=multi_key),
        load_csv(io.StringIO(MULTI_KEY_ROW_REMOVED_AND_CHANGE), key=multi_key)
    )
    assert {
        "changed": [
            {
                "key": ("CUST-001", "2022-01-01 10:00:00"),
                "changes": {"Quantity": ["2", "3"]}
            }
        ],
        "removed": [
            {"Customer ID": "CUST-001", "Timestamp": "2022-01-02 11:00:00", "Product Name": "Table", "Quantity": "1"}
        ],
        "added": [],
        "columns_added": [],
        "columns_removed": [],
    } == diff


def test_multi_key_columns_changed():
    diff = compare(
        load_csv(io.StringIO(MULTI_KEY_BASE), key=multi_key),
        load_csv(io.StringIO(MULTI_KEY_COLUMN_ADD), key=multi_key)
    )
    assert {
        "changed": [],
        "removed": [],
        "added": [],
        "columns_added": ["Price"],
        "columns_removed": ["Quantity"],
    } == diff

def test_multi_key_primary_key_removed_and_added():
    diff = compare(
        load_csv(io.StringIO(MULTI_KEY_BASE), key=multi_key),
        load_csv(io.StringIO(MULTI_KEY_PRIMARY_KEY_CHANGED), key=multi_key)
    )
    assert {
        "changed": [],
        "removed": [{"Customer ID": "CUST-001", "Timestamp": "2022-01-02 11:00:00", "Product Name": "Table", "Quantity": "1"}],
        "added": [{"Customer ID": "CUST-003", "Timestamp": "2022-01-02 11:00:00", "Product Name": "Table", "Quantity": "1"}],
        "columns_added": [],
        "columns_removed": [],
    } == diff
