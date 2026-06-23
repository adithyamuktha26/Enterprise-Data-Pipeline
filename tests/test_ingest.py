"""Tests for the ingest module."""

import sys
from pathlib import Path
import pandas as pd

# Add src to path so we can import it
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ingest import read_csv_file


def test_read_csv_success():
    """Test reading a valid CSV file."""
    # Create a test CSV
    test_data = pd.DataFrame(
        {
            "name": ["Alice", "Bob"],
            "email": ["alice@apple.com", "bob@apple.com"],
            "department": ["Engineering", "Sales"],
            "salary": [120000, 95000],
        }
    )

    test_path = Path("data/raw/test_employees.csv")
    test_path.parent.mkdir(parents=True, exist_ok=True)
    test_data.to_csv(test_path, index=False)

    # Test our function
    result = read_csv_file(str(test_path))

    assert len(result) == 2
    assert list(result.columns) == ["name", "email", "department", "salary"]
    print("✅ test_read_csv_success passed")

    # Cleanup
    test_path.unlink()


def test_read_csv_file_not_found():
    """Test that missing file raises FileNotFoundError."""
    try:
        read_csv_file("data/raw/nonexistent.csv")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        print("✅ test_read_csv_file_not_found passed")


if __name__ == "__main__":
    test_read_csv_success()
    test_read_csv_file_not_found()
    print("\n🎉 All tests passed!")
