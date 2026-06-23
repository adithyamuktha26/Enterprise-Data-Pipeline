#!/usr/bin/env python3
"""
Run the pipeline scheduler.
Usage:
    python run_scheduler.py daily        # Run every day at 9:00 AM
    python run_scheduler.py hourly       # Run every hour
    python run_scheduler.py minute       # Run every minute (testing)
    python run_scheduler.py now          # Run once immediately
"""

import sys
from src.scheduler import PipelineScheduler


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_scheduler.py [daily|hourly|minute|now]")
        print("Examples:")
        print("  python run_scheduler.py daily    # Runs at 9:00 AM daily")
        print("  python run_scheduler.py hourly   # Runs every hour")
        print("  python run_scheduler.py minute   # Runs every minute (test)")
        print("  python run_scheduler.py now      # Run once immediately")
        sys.exit(1)

    mode = sys.argv[1].lower()
    scheduler = PipelineScheduler()

    if mode == "daily":
        scheduler.schedule_daily("09:00")
        scheduler.start()

    elif mode == "hourly":
        scheduler.schedule_hourly()
        scheduler.start()

    elif mode == "minute":
        scheduler.schedule_every_minute()
        scheduler.start()

    elif mode == "now":
        scheduler.run_now()
        print("\n✅ Manual run complete. Scheduler not started.")

    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
