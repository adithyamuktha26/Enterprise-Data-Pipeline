"""
Scheduler Module
Uses APScheduler to run the pipeline automatically at set intervals.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from main import run_pipeline


class PipelineScheduler:
    """
    Manages automatic execution of the data pipeline.
    Runs in the background without blocking your terminal.
    """

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.jobs = {}  # Track scheduled jobs by name
        self.run_history = []  # Keep log of all runs

    def schedule_daily(
        self, time_str: str = "09:00", filepath: str = "data/raw/employees.csv"
    ):
        """
        Run the pipeline every day at a specific time.

        Args:
            time_str: Time in "HH:MM" format (24-hour)
            filepath: Which file to process
        """
        hour, minute = map(int, time_str.split(":"))

        job = self.scheduler.add_job(
            func=self._run_job,
            trigger=CronTrigger(hour=hour, minute=minute),
            id="daily_pipeline",
            args=[filepath],
            replace_existing=True,
        )

        self.jobs["daily"] = job
        print(f"📅 Scheduled daily run at {time_str} for {filepath}")
        return job

    def schedule_hourly(self, filepath: str = "data/raw/employees.csv"):
        """
        Run the pipeline every hour.
        Good for testing or high-frequency data sources.
        """
        job = self.scheduler.add_job(
            func=self._run_job,
            trigger=IntervalTrigger(hours=1),
            id="hourly_pipeline",
            args=[filepath],
            replace_existing=True,
        )

        self.jobs["hourly"] = job
        print(f"⏰ Scheduled hourly runs for {filepath}")
        return job

    def schedule_every_minute(self, filepath: str = "data/raw/employees.csv"):
        """
        Run every minute. ONLY for testing — never in production.
        """
        job = self.scheduler.add_job(
            func=self._run_job,
            trigger=IntervalTrigger(minutes=1),
            id="minute_pipeline",
            args=[filepath],
            replace_existing=True,
        )

        self.jobs["minute"] = job
        print(f"⚡ Scheduled every-minute runs for {filepath} (TEST ONLY)")
        return job

    def run_now(self, filepath: str = "data/raw/employees.csv"):
        """
        Run the pipeline immediately, once.
        """
        print(f"\n🚀 MANUAL RUN: {datetime.now()}")
        self._run_job(filepath)

    def _run_job(self, filepath: str):
        """
        Internal method that executes the pipeline and logs results.
        """
        run_time = datetime.now()
        print(f"\n{'=' * 60}")
        print(f"⏰ SCHEDULED RUN TRIGGERED: {run_time}")
        print(f"{'=' * 60}")

        try:
            stats = run_pipeline(filepath)
            self.run_history.append(
                {
                    "time": run_time,
                    "status": "success",
                    "file": filepath,
                    "stats": stats,
                }
            )
            print(f"✅ Scheduled run completed successfully")

        except Exception as e:
            self.run_history.append(
                {
                    "time": run_time,
                    "status": "failed",
                    "file": filepath,
                    "error": str(e),
                }
            )
            print(f"❌ Scheduled run failed: {e}")

    def start(self):
        """Start the scheduler (runs in background)."""
        self.scheduler.start()
        print(f"\n✅ Scheduler started. Press Ctrl+C to stop.")
        print(f"   Active jobs: {len(self.scheduler.get_jobs())}")

        try:
            # Keep the main thread alive so scheduler can run
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            self.shutdown()

    def shutdown(self):
        """Stop the scheduler gracefully."""
        self.scheduler.shutdown()
        print(f"\n🛑 Scheduler stopped.")
        print(f"   Total runs: {len(self.run_history)}")
        successes = sum(1 for r in self.run_history if r["status"] == "success")
        print(
            f"   Successful: {successes} | Failed: {len(self.run_history) - successes}"
        )

    def get_status(self):
        """Print current scheduler status."""
        jobs = self.scheduler.get_jobs()
        print(f"\n📊 SCHEDULER STATUS")
        print(f"   Active jobs: {len(jobs)}")
        for job in jobs:
            print(f"   - {job.id}: Next run at {job.next_run_time}")
        print(f"   Run history: {len(self.run_history)} total runs")
