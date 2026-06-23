"""
Main Pipeline Module
Orchestrates the entire data flow:
1. Ingest raw data → 2. Validate → 3. Store in DB → 4. Generate report
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ingest import read_csv_file, read_excel_file
from validate import validate_dataframe, ValidationResult
from database import DatabaseManager
from notifier import Notifier


class DataPipeline:
    """
    The main pipeline class. One instance = one complete run.
    """

    def __init__(self, db_path: str = "data/enterprise.db"):
        self.db = DatabaseManager(db_path=db_path)
        self.run_time = datetime.now()
        self.stats = {
            "file_processed": None,
            "total_rows": 0,
            "valid_rows": 0,
            "invalid_rows": 0,
            "stored_in_db": 0,
            "errors": [],
        }

    def process_file(self, filepath: str) -> dict:
        """
        Process a single data file through the entire pipeline.

        Args:
            filepath: Path to CSV or Excel file

        Returns:
            Dictionary with full run statistics
        """
        print(f"\n{'=' * 60}")
        print(f"🚀 PIPELINE STARTED: {self.run_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 60}")

        # Step 1: INGEST
        print(f"\n📥 STEP 1: INGESTING DATA")
        print(f"   File: {filepath}")

        try:
            if filepath.lower().endswith(".csv"):
                df = read_csv_file(filepath)
            elif filepath.lower().endswith((".xlsx", ".xls")):
                df = read_excel_file(filepath)
            else:
                raise ValueError("File must be .csv, .xlsx, or .xls")
        except Exception as e:
            self.stats["errors"].append(f"Ingest failed: {str(e)}")
            print(f"   ❌ FAILED: {e}")
            return self.stats

        self.stats["file_processed"] = Path(filepath).name
        self.stats["total_rows"] = len(df)
        print(f"   ✅ Loaded {len(df)} rows")

        # Step 2: VALIDATE
        print(f"\n🔍 STEP 2: VALIDATING DATA")

        try:
            validation = validate_dataframe(df)
        except Exception as e:
            self.stats["errors"].append(f"Validation failed: {str(e)}")
            print(f"   ❌ FAILED: {e}")
            return self.stats

        self.stats["valid_rows"] = validation.valid_count
        self.stats["invalid_rows"] = validation.invalid_count

        # Step 3: STORE IN DATABASE
        print(f"\n💾 STEP 3: STORING IN DATABASE")

        if validation.valid_records:
            # Convert Pydantic models to plain dicts for the database
            records = [r.model_dump() for r in validation.valid_records]
            stored = self.db.add_employees_batch(records)
            self.stats["stored_in_db"] = stored
            print(f"   ✅ Stored {stored} records in database")
        else:
            print(f"   ⚠️  No valid records to store")

        # Step 4: GENERATE SUMMARY
        print(f"\n{'=' * 60}")
        print(f"📊 PIPELINE COMPLETE")
        print(f"{'=' * 60}")
        print(self._format_summary())

        return self.stats

    def _format_summary(self) -> str:
        """Format a nice summary of the pipeline run."""
        s = self.stats
        return (
            f"   File processed: {s['file_processed']}\n"
            f"   Total rows read: {s['total_rows']}\n"
            f"   ✅ Valid records: {s['valid_rows']}\n"
            f"   ❌ Invalid records: {s['invalid_rows']}\n"
            f"   💾 Stored in DB: {s['stored_in_db']}\n"
            f"   Success rate: {(s['valid_rows'] / s['total_rows'] * 100):.1f}%"
            if s["total_rows"] > 0
            else "   No data processed"
        )

    def get_department_report(self) -> str:
        """Get a formatted department statistics report."""
        stats = self.db.get_department_stats()

        lines = ["\n📈 DEPARTMENT REPORT", "=" * 40]
        for s in stats:
            lines.append(
                f"   {s['department']:<15} | "
                f"Count: {s['count']:<3} | "
                f"Avg: ${s['avg_salary']:>10,.2f} | "
                f"Total: ${s['total_salary']:>12,.2f}"
            )
        return "\n".join(lines)

    def close(self):
        """Clean up resources."""
        self.db.close()


def run_pipeline(filepath: str, notify: bool = False):
    """
    Run the pipeline with optional notifications.

    Args:
        filepath: Path to data file
        notify: If True, sends console report (email/Slack need setup)
    """
    pipeline = DataPipeline()
    notifier = Notifier()

    try:
        stats = pipeline.process_file(filepath)
        dept_stats = pipeline.db.get_department_stats()

        # Always print department report
        print(pipeline.get_department_report())

        # Send notification if requested
        if notify:
            notifier.console_report(stats, dept_stats)

            # Example: To enable real email, uncomment and configure:
            # notifier.configure_email("your@gmail.com", "your_app_password")
            # notifier.send_email_report("boss@apple.com", "Pipeline Report", stats, dept_stats)

            # Example: To enable Slack, uncomment and configure:
            # notifier.configure_slack("https://hooks.slack.com/services/YOUR/WEBHOOK/URL")
            # notifier.send_slack_message(f"Pipeline complete! {stats['valid_rows']} records processed.")

    finally:
        pipeline.close()

    return stats


# def run_pipeline(filepath: str):
#     """
#     Convenience function to run the pipeline on a file.

#     Usage:
#         python src/main.py data/raw/employees.csv
#     """
#     pipeline = DataPipeline()

#     try:
#         stats = pipeline.process_file(filepath)
#         print(pipeline.get_department_report())
#     finally:
#         pipeline.close()

#     return stats


if __name__ == "__main__":
    # If run directly, expect a filepath as argument
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        run_pipeline(filepath)
    else:
        print("Usage: python src/main.py <path_to_file>")
        print("Example: python src/main.py data/raw/employees.csv")
