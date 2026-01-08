#!/usr/bin/env python3
"""
Aggregate mutation testing results from all module databases.

Queries all SQLite databases and calculates aggregated metrics including
overall mutation score and per-module breakdown.
"""

import glob
import json
import os
import sqlite3


def query_database(db_file):
    """Query a cosmic-ray database and return mutation statistics."""
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Get total mutations
        cursor.execute("SELECT COUNT(*) FROM work")
        total = cursor.fetchone()[0]

        # Get killed mutations
        cursor.execute("SELECT COUNT(*) FROM work WHERE outcome = 'killed'")
        killed = cursor.fetchone()[0]

        # Get survived mutations
        cursor.execute("SELECT COUNT(*) FROM work WHERE outcome = 'survived'")
        survived = cursor.fetchone()[0]

        # Get pending mutations
        cursor.execute("SELECT COUNT(*) FROM work WHERE outcome IS NULL")
        pending = cursor.fetchone()[0]

        conn.close()

        return {
            "total": total,
            "killed": killed,
            "survived": survived,
            "pending": pending
        }
    except Exception as e:
        print(f"Error querying database {db_file}: {e}", file=os.sys.stderr)
        return {
            "total": 0,
            "killed": 0,
            "survived": 0,
            "pending": 0
        }


def aggregate_results():
    """Aggregate results from all module databases."""
    db_files = glob.glob("db-*.sqlite")

    if not db_files:
        print("⚠️ No database files found")
        return None

    module_results = {}
    total_mutations = 0
    total_killed = 0
    total_survived = 0
    total_pending = 0

    for db_file in db_files:
        module_name = db_file.replace("db-", "").replace(".sqlite", "")
        stats = query_database(db_file)

        module_results[module_name] = stats

        total_mutations += stats["total"]
        total_killed += stats["killed"]
        total_survived += stats["survived"]
        total_pending += stats["pending"]

    # Calculate overall mutation score
    completed = total_killed + total_survived
    if completed > 0:
        mutation_score = (total_killed / completed) * 100
    else:
        mutation_score = 0

    # Calculate per-module scores
    module_scores = {}
    for module, stats in module_results.items():
        mod_completed = stats["killed"] + stats["survived"]
        if mod_completed > 0:
            module_scores[module] = {
                "score": (stats["killed"] / mod_completed) * 100,
                "killed": stats["killed"],
                "survived": stats["survived"],
                "total": stats["total"],
                "completed": mod_completed
            }
        else:
            module_scores[module] = {
                "score": 0,
                "killed": stats["killed"],
                "survived": stats["survived"],
                "total": stats["total"],
                "completed": 0
            }

    aggregated = {
        "overall": {
            "total_mutations": total_mutations,
            "killed": total_killed,
            "survived": total_survived,
            "pending": total_pending,
            "completed": completed,
            "mutation_score": mutation_score
        },
        "modules": module_scores,
        "module_details": module_results
    }

    return aggregated


def generate_summary_report(aggregated):
    """Generate a human-readable summary report."""
    print("\n" + "=" * 60)
    print("MUTATION TESTING RESULTS SUMMARY")
    print("=" * 60)

    overall = aggregated["overall"]
    print("\nOverall Statistics:")
    print(f"  Total Mutations: {overall['total_mutations']}")
    print(f"  Completed: {overall['completed']}")
    print(f"  Pending: {overall['pending']}")
    print(f"  Killed: {overall['killed']}")
    print(f"  Survived: {overall['survived']}")
    print(f"  Mutation Score: {overall['mutation_score']:.2f}%")

    print("\nPer-Module Breakdown:")
    for module, scores in aggregated["modules"].items():
        print(f"  {module}:")
        print(f"    Score: {scores['score']:.2f}%")
        print(f"    Killed: {scores['killed']}/{scores['completed']}")
        print(f"    Survived: {scores['survived']}")
        print(f"    Total: {scores['total']}")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    import sys

    try:
        aggregated = aggregate_results()

        if aggregated is None:
            sys.exit(1)

        # Generate summary report
        generate_summary_report(aggregated)

        # Save aggregated results to JSON
        os.makedirs("mutation-reports/aggregated", exist_ok=True)
        output_file = "mutation-reports/aggregated/summary.json"

        with open(output_file, "w") as f:
            json.dump(aggregated, f, indent=2)

        print(f"✅ Aggregated results saved to {output_file}")

        sys.exit(0)
    except Exception as e:
        print(f"❌ Error aggregating results: {e}", file=os.sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

