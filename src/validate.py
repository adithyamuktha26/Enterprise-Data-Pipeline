"""
Data Validation Module
Uses Pydantic to validate enterprise data before database storage.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
import pandas as pd


class EmployeeRecord(BaseModel):
    """
    Validates a single employee record.
    Each field has rules that must pass for the record to be accepted.
    """

    name: str = Field(
        ..., min_length=2, max_length=100, description="Employee full name"
    )
    email: EmailStr = Field(..., description="Valid company email")
    department: str = Field(..., min_length=1, description="Department name")
    salary: float = Field(..., gt=0, description="Annual salary (must be positive)")
    employee_id: Optional[str] = Field(None, description="Optional employee ID")

    @validator("name")
    def name_must_not_be_blank(cls, v):
        """Ensure name isn't just whitespace."""
        if not v.strip():
            raise ValueError("Name cannot be blank or whitespace only")
        return v.strip()

    @validator("department")
    def department_must_be_valid(cls, v):
        """Ensure department is a known department."""
        valid_departments = {
            "Engineering",
            "Sales",
            "Marketing",
            "HR",
            "Finance",
            "Operations",
            "Legal",
            "IT",
        }
        if v not in valid_departments:
            raise ValueError(f"Department must be one of: {valid_departments}")
        return v


class ValidationResult:
    """Holds the results of validating a batch of records."""

    def __init__(self):
        self.valid_records: List[EmployeeRecord] = []
        self.invalid_records: List[dict] = []
        self.errors: List[str] = []

    @property
    def valid_count(self) -> int:
        return len(self.valid_records)

    @property
    def invalid_count(self) -> int:
        return len(self.invalid_records)

    def summary(self) -> str:
        """Returns a human-readable summary of validation results."""
        total = self.valid_count + self.invalid_count
        return (
            f"📊 Validation Summary:\n"
            f"   Total records: {total}\n"
            f"   ✅ Valid: {self.valid_count}\n"
            f"   ❌ Invalid: {self.invalid_count}\n"
            f"   Success rate: {(self.valid_count / total * 100):.1f}%"
            if total > 0
            else "No records processed"
        )


def validate_dataframe(df: pd.DataFrame) -> ValidationResult:
    """
    Validates every row in a DataFrame against EmployeeRecord rules.

    Args:
        df: pandas DataFrame with employee data

    Returns:
        ValidationResult with valid/invalid records and error details
    """
    result = ValidationResult()

    # Check required columns exist
    required_columns = {"name", "email", "department", "salary"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    # Validate each row
    for index, row in df.iterrows():
        row_dict = row.to_dict()

        try:
            # Try to create a valid EmployeeRecord
            record = EmployeeRecord(**row_dict)
            result.valid_records.append(record)

        except Exception as e:
            # Record failed validation — save it with error info
            result.invalid_records.append(
                {"row_index": index, "data": row_dict, "error": str(e)}
            )
            result.errors.append(f"Row {index}: {str(e)}")

    print(result.summary())
    return result
