"""Compare current Week 5 outputs with a fresh run that has no prior outputs.

Run after src/main.py. Only the temporary directory created by this command
is removed; original inputs and deliverables are never deleted.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analyze_week5 import (GOV_EXCERPT, PRIOR_LOG, RAW, REFERENCE, REGISTRY,
                                SOURCE_MAPPING, file_sha256, write_json)


def main() -> None:
    manifest_path = ROOT / "outputs/week5_manifest+ho_so_dau_ra.json"
    baseline = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = baseline["deterministic_output_sha256"]
    for name, digest in expected.items():
        if file_sha256(ROOT / name) != digest:
            raise ValueError(f"Output changed since pipeline run: {name}; rerun src/main.py")
    source_files = [RAW, REFERENCE, REGISTRY, PRIOR_LOG, GOV_EXCERPT, SOURCE_MAPPING]
    code_files = sorted((ROOT / "src").glob("*.py"))
    input_hashes = {p.as_posix(): file_sha256(ROOT / p) for p in source_files}
    code_hashes = {p.relative_to(ROOT).as_posix(): file_sha256(p) for p in code_files}
    # Stage raw inputs and code only; no processed data, tables or old notebooks.
    scratch_parent = (ROOT / "outputs/_review").resolve()
    scratch_parent.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="week5_verify_", dir=scratch_parent)).resolve()
    try:
        for relative in source_files:
            target = scratch / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        (scratch / "src").mkdir()
        for path in code_files:
            shutil.copyfile(path, scratch / "src" / path.name)
        run = subprocess.run([sys.executable, "-X", "utf8", "src/main.py"],
                             cwd=scratch, capture_output=True, text=True, encoding="utf-8")
        if run.returncode:
            raise RuntimeError(run.stdout + run.stderr)
        fresh = json.loads((scratch / "outputs/week5_manifest+ho_so_dau_ra.json").read_text(encoding="utf-8"))
        actual = fresh["deterministic_output_sha256"]
        comparisons = {name: expected.get(name) == actual.get(name)
                       for name in sorted(set(expected) | set(actual))}
        result = {
            "method": "Compare current verified outputs with a clean directory containing only raw inputs, source documentation and Python code.",
            "environment": fresh["environment"],
            "input_sha256": input_hashes,
            "code_sha256": code_hashes,
            "output_sha256": actual,
            "files_compared": len(comparisons),
            "same_sha256_by_file": comparisons,
            "all_equal": all(comparisons.values()),
            "roundtrip_validation": fresh["validation"],
            "excluded_from_comparison": ["outputs/week5_manifest+ho_so_dau_ra.json (runtime_seconds varies)"],
            "fresh_run_stdout": run.stdout.replace(str(scratch), "<isolated_root>"),
        }
        write_json(result, ROOT / "outputs/week5_verification+kiem_tra_tai_lap.json")
        if not result["all_equal"] or not all(fresh["validation"].values()):
            raise AssertionError("Reproducibility check failed; see outputs/week5_verification+kiem_tra_tai_lap.json")
        print(f"PASS: {len(comparisons)} output files have identical SHA-256 in a clean run.")
        print("Evidence: outputs/week5_verification+kiem_tra_tai_lap.json")
    finally:
        # Resolve and constrain recursive cleanup to this command's new scratch directory.
        if scratch.parent != scratch_parent or not scratch.name.startswith("week5_verify_"):
            raise ValueError("Refusing cleanup outside the verification workspace")
        shutil.rmtree(scratch)


if __name__ == "__main__":
    main()
