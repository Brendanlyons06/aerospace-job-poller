from ..feeds import ashby_internships_us

COMPANY_NAME = "Applied Intuition"
CAREERS_URL = "https://jobs.ashbyhq.com/applied"


def fetch_jobs() -> list[dict]:
    # Internships here are titled "Research Intern - <ML topic>" (reinforcement
    # learning, 3D vision, foundation models) — all ML research, but none name
    # software or ML, so the generic SWE/ML title check would drop every one.
    return ashby_internships_us("applied", require_swe_ml=False)
