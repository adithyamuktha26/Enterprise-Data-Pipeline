"""
Database Module
Handles all database operations using SQLAlchemy + SQLite.
SQLite is a file-based database — no server needed, perfect for beginners.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from pathlib import Path
from typing import List

# Create the base class for our tables
Base = declarative_base()


class Employee(Base):
    """
    Database table representing an employee.
    Each instance = one row in the database.
    """

    __tablename__ = "employees"  # Name of the table

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), nullable=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    department = Column(String(50), nullable=False)
    salary = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Employee(name='{self.name}', dept='{self.department}', salary={self.salary})>"


class DatabaseManager:
    """
    Manages the database connection and all CRUD operations.
    CRUD = Create, Read, Update, Delete
    """

    def __init__(self, db_path: str = "data/enterprise.db"):
        """
        Initialize the database manager.

        Args:
            db_path: Where the SQLite database file lives
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Create the database engine (the "bridge" to SQLite)
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)

        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)

        # Create a session factory (for adding/querying data)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        print(f"✅ Database initialized at: {db_path}")

    def add_employee(
        self,
        name: str,
        email: str,
        department: str,
        salary: float,
        employee_id: str = None,
    ) -> Employee:
        """Add a single employee, or return existing if email already exists."""
        existing = self.session.query(Employee).filter_by(email=email).first()
        if existing:
            print(f"   ⚠️  Employee with email {email} already exists, skipping")
            return existing

        employee = Employee(
            name=name,
            email=email,
            department=department,
            salary=salary,
            employee_id=employee_id,
        )
        self.session.add(employee)
        self.session.commit()
        return employee

    def add_employees_batch(self, records: List[dict]) -> int:
        """
        Add multiple employees, skipping duplicates by email.
        Returns number of NEW employees added.
        """
        added = 0
        skipped = 0

        for record in records:
            # Check if email already exists
            existing = (
                self.session.query(Employee).filter_by(email=record["email"]).first()
            )

            if existing:
                skipped += 1
                continue  # Skip this one, don't crash

            emp = Employee(
                name=record["name"],
                email=record["email"],
                department=record["department"],
                salary=record["salary"],
                employee_id=record.get("employee_id"),
            )
            self.session.add(emp)
            added += 1

        self.session.commit()

        if skipped > 0:
            print(f"   ⚠️  Skipped {skipped} duplicate records")
        print(f"   ✅ Added {added} new records")

        return added

    def get_all_employees(self) -> List[Employee]:
        """Return all employees in the database."""
        return self.session.query(Employee).all()

    def get_employees_by_department(self, department: str) -> List[Employee]:
        """Filter employees by department."""
        return self.session.query(Employee).filter_by(department=department).all()

    def get_department_stats(self) -> List[dict]:
        """
        Get salary statistics per department.
        Returns list of dicts with department, count, avg_salary, total_salary.
        """
        from sqlalchemy import func

        results = (
            self.session.query(
                Employee.department,
                func.count(Employee.id).label("count"),
                func.avg(Employee.salary).label("avg_salary"),
                func.sum(Employee.salary).label("total_salary"),
            )
            .group_by(Employee.department)
            .all()
        )

        return [
            {
                "department": r.department,
                "count": r.count,
                "avg_salary": round(r.avg_salary, 2),
                "total_salary": round(r.total_salary, 2),
            }
            for r in results
        ]

    def get_employee_count(self) -> int:
        """Return total number of employees."""
        return self.session.query(Employee).count()

    def close(self):
        """Close the database connection."""
        self.session.close()
        print("✅ Database connection closed")
