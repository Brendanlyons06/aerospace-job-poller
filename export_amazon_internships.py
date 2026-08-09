"""Export Amazon's current internship-search listings without running the poller.

Run from this repository:
    python3 -P export_amazon_internships.py

This writes ``amazon_internships.json`` beside the script.  It does not read
or write ``jobs.db`` and never sends notifications.
"""

import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def _load_amazon_adapter():
    """Load the repo as a package so the adapter's relative imports work."""
    package_name = "job_poller_export"
    spec = importlib.util.spec_from_file_location(
        package_name,
        ROOT / "__init__.py",
        submodule_search_locations=[str(ROOT)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load the Job-poller package")
    package = importlib.util.module_from_spec(spec)
    sys.modules[package_name] = package
    spec.loader.exec_module(package)

    from job_poller_export.companies.amazon import CAREERS_URL, fetch_jobs

    return CAREERS_URL, fetch_jobs


def main() -> None:
    careers_url, fetch_jobs = _load_amazon_adapter()
    jobs = fetch_jobs()
    output_path = ROOT / "amazon_internships.json"
    output_path.write_text(
        json.dumps(
            {
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "source": careers_url,
                "count": len(jobs),
                "jobs": jobs,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(jobs)} Amazon internship listings to {output_path}")


if __name__ == "__main__":
    main()
