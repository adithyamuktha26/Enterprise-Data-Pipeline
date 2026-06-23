"""Tests for the validation module."""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from validate import validate_dataframe, EmployeeRecord


def test_valid_record():
    """Test that a perfect record passes."""
    record = EmployeeRecord(
        name="Tim Cook",
        email="tim@apple.com",
        department="Engineering",
        salary=50000000,
    )
    assert record.name == "Tim Cook"
    print("\n✅ test_valid_record passed")


def test_invalid_email():
    """Test that bad email is rejected."""
    try:
        EmployeeRecord(
            name="Bad User",
            email="not-an-email",
            department="Engineering",
            salary=100000,
        )
        assert False, "Should have raised validation error"
    except Exception:
        print("✅ test_invalid_email passed")


def test_validate_dataframe():
    """Test validating a batch of records."""
    df = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Bad", "Charlie"],
            "email": [
                "alice@apple.com",
                "bob@apple.com",
                "bad-email",
                "charlie@apple.com",
            ],
            "department": ["Engineering", "Sales", "Engineering", "FakeDept"],
            "salary": [120000, 95000, -5000, 80000],
        }
    )

    result = validate_dataframe(df)

    # Alice and Bob should be valid
    # Bad has bad email and negative salary
    # Charlie has invalid department
    assert result.valid_count == 2  # Alice and Bob
    assert result.invalid_count == 2  # Bad and Charlie
    print("✅ test_validate_dataframe passed")


if __name__ == "__main__":
    test_valid_record()
    test_invalid_email()
    test_validate_dataframe()
    print("\n🎉 All validation tests passed!\n")
