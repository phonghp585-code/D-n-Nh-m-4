"""Run Week 5 from the immutable raw CSV and the versioned 2023 reference table."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analyze_week5 import ROOT, run_week5


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Week 5 exam-score cleaning and merge pipeline")
    parser.add_argument("--output-root", type=Path, default=ROOT,
                        help="Optional output root for an isolated reproducibility run")
    args = parser.parse_args()
    metrics = run_week5(ROOT, args.output_root)
    merge = metrics["merge"]
    print("Week 5 pipeline complete")
    print(f"Rows: {metrics['source']['main_rows']:,} raw -> "
          f"{metrics['processing']['rows_after_exact_duplicate_removal']:,} processed")
    print(f"Council match: {merge['matched_rows']:,} matched / "
          f"{merge['unmatched_rows']:,} unmatched ({merge['record_match_rate_pct']:.4f}%)")
    print(f"Output CSV: {args.output_root / 'data/processed/week5_final+du_lieu_cuoi.csv'}")
    print(f"Report: {args.output_root / 'docs/week5_report+bao_cao.md'}")
    print(f"Manifest: {args.output_root / 'outputs/week5_manifest+ho_so_dau_ra.json'}")


if __name__ == "__main__":
    main()
