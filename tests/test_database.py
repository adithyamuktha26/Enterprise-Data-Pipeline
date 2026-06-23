"""Tests for the database module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database import DatabaseManager, Employee


def test_database_creation():
    """Test that database and tables are created."""
    db = DatabaseManager(db_path="data/test_enterprise.db")
    count = db.get_employee_count()
    assert count == 0  # Should start empty
    print(f"✅ Database created, initial count: {count}")
    db.close()


def test_add_single_employee():
    """Test adding one employee."""
    db = DatabaseManager(db_path="data/test_enterprise.db")

    emp = db.add_employee(
        name="Tim Cook",
        email="tim@apple.com",
        department="Engineering",
        salary=50000000,
    )

    assert emp.name == "Tim Cook"
    assert emp.email == "tim@apple.com"
    print(f"✅ Added employee: {emp}")
    db.close()


def test_add_batch():
    """Test adding multiple employees at once."""
    db = DatabaseManager(db_path="data/test_enterprise.db")

    records = [
        {
            "name": "Alice",
            "email": "alice@apple.com",
            "department": "Engineering",
            "salary": 120000,
        },
        {
            "name": "Bob",
            "email": "bob@apple.com",
            "department": "Sales",
            "salary": 95000,
        },
        {
            "name": "Charlie",
            "email": "charlie@apple.com",
            "department": "Engineering",
            "salary": 130000,
        },
    ]

    count = db.add_employees_batch(records)
    assert count == 3
    print(f"✅ Added {count} employees in batch")

    total = db.get_employee_count()
    print(f"✅ Total employees in DB: {total}")

    db.close()


def test_department_stats():
    """Test getting department statistics."""
    db = DatabaseManager(db_path="data/test_enterprise.db")

    stats = db.get_department_stats()
    print(f"✅ Department stats: {stats}")

    # Engineering should have 2 people (Tim from test 2 + Alice + Charlie)
    engineering = [s for s in stats if s["department"] == "Engineering"]
    assert len(engineering) > 0
    print(f"✅ Engineering department found in stats")

    db.close()


def test_filter_by_department():
    """Test filtering employees."""
    db = DatabaseManager(db_path="data/test_enterprise.db")

    sales = db.get_employees_by_department("Sales")
    assert len(sales) >= 1
    print(f"✅ Found {len(sales)} Sales employees")

    db.close()


if __name__ == "__main__":
    test_database_creation()
    test_add_single_employee()
    test_add_batch()
    test_department_stats()
    test_filter_by_department()
    print("\n🎉 All database tests passed!")
