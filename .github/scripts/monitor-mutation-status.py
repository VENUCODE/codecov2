#!/usr/bin/env python3
"""
Monitor mutation testing progress across all modules.

Continuously loops checking database files and reporting progress until all jobs complete.
Uses cr-report and grep to extract status information.
"""

import glob
import json
import os
import subprocess
import time


def run_cr_report(db_file):
    """Run cr-report and return output."""
    try:
        result = subprocess.run(
            ["cr-report", db_file, "--show-pending"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running cr-report on {db_file}: {e}", file=os.sys.stderr)
        return ""
    except FileNotFoundError:
        print("cr-report not found. Make sure cosmic-ray is installed.", file=os.sys.stderr)
        return ""


def extract_status_with_grep(output):
    """Extract status information using grep-like pattern matching."""
    status = {
        "total": 0,
        "complete": 0,
        "surviving": 0,
        "pending": 0
    }

    lines = output.split('\n')
    for line in lines:
        if "total jobs:" in line.lower():
            # Extract number after "total jobs:"
            parts = line.split()
            for i, part in enumerate(parts):
                if part.lower() == "total" and i + 2 < len(parts) and parts[i+1].lower() == "jobs:":
                    try:
                        status["total"] = int(parts[i+2])
                    except (ValueError, IndexError):
                        pass

        if "complete:" in line.lower():
            # Extract number after "complete:"
            parts = line.split()
            for i, part in enumerate(parts):
                if part.lower() == "complete:":
                    try:
                        status["complete"] = int(parts[i+1])
                    except (ValueError, IndexError):
                        pass

        if "surviving mutants:" in line.lower():
            # Extract number after "surviving mutants:"
            parts = line.split()
            for i, part in enumerate(parts):
                if part.lower() == "surviving" and i + 1 < len(parts) \
                    and parts[i+1].lower().startswith("mutants"):
                    try:
                        # Look for number in parentheses or after colon
                        for j in range(i, min(i+5, len(parts))):
                            if "(" in parts[j] and ")" in parts[j]:
                                num_str = parts[j].strip("()")
                                status["surviving"] = int(num_str.split()[0])
                                break
                    except (ValueError, IndexError):
                        pass

    status["pending"] = status["total"] - status["complete"]
    return status


def find_database_files(pattern="db-*.sqlite"):
    """Find all database files matching the pattern."""
    files = glob.glob(pattern)
    return [f for f in files if os.path.isfile(f)]


def monitor_status(check_interval=30, max_wait_time=3600):
    """Monitor mutation testing status in a loop."""
    start_time = time.time()
    iteration = 0

    print("Starting mutation testing status monitor...")
    print(f"Check interval: {check_interval} seconds")
    print(f"Max wait time: {max_wait_time} seconds")
    print("-" * 60)

    while True:
        iteration += 1
        elapsed = time.time() - start_time

        if elapsed > max_wait_time:
            print(f"\n⚠️ Timeout reached after {max_wait_time} seconds")
            break

        db_files = find_database_files()

        if not db_files:
            print(f"[{iteration}] No database files found yet. Waiting...")
            time.sleep(check_interval)
            continue

        all_status = {}
        total_jobs = 0
        total_complete = 0
        total_surviving = 0

        for db_file in db_files:
            module_name = db_file.replace("db-", "").replace(".sqlite", "")
            output = run_cr_report(db_file)

            if output:
                status = extract_status_with_grep(output)
                all_status[module_name] = status
                total_jobs += status["total"]
                total_complete += status["complete"]
                total_surviving += status["surviving"]

        # Calculate completion percentage
        if total_jobs > 0:
            completion_pct = (total_complete / total_jobs) * 100
            remaining = total_jobs - total_complete
        else:
            completion_pct = 0
            remaining = 0

        # Print status update
        print(f"\n[{iteration}] Status Update (Elapsed: {elapsed:.0f}s)")
        print(f"Total Jobs: {total_jobs}")
        print(f"Completed: {total_complete}")
        print(f"Remaining: {remaining}")
        print(f"Completion: {completion_pct:.1f}%")
        print(f"Surviving Mutants: {total_surviving}")

        # Per-module breakdown
        if all_status:
            print("\nPer-module status:")
            for module, status in all_status.items():
                if status["total"] > 0:
                    mod_pct = (status["complete"] / status["total"]) * 100
                    print(f"  {module}: {status['complete']}/{status['total']} ({mod_pct:.1f}%)")

        # Check if all complete
        if total_jobs > 0 and total_complete == total_jobs:
            print("\n✅ All mutation testing jobs completed!")
            break

        # Sleep before next check
        time.sleep(check_interval)

    # Output final summary JSON
    summary = {
        "total_jobs": total_jobs,
        "completed": total_complete,
        "remaining": remaining,
        "surviving": total_surviving,
        "completion_percentage": completion_pct,
        "modules": all_status
    }

    os.makedirs("mutation-reports", exist_ok=True)
    with open("mutation-reports/status-summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\nStatus summary saved to mutation-reports/status-summary.json")
    return summary


if __name__ == "__main__":
    import sys

    check_interval = int(os.environ.get("CHECK_INTERVAL", "30"))
    max_wait = int(os.environ.get("MAX_WAIT_TIME", "3600"))

    try:
        summary = monitor_status(check_interval=check_interval, max_wait_time=max_wait)
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n⚠️ Monitoring interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during monitoring: {e}", file=os.sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

