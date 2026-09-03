"""Search profiles and the aerospace/mechanical company target list.

The original repository is a broad U.S. SWE/ML internship watcher.  A
profile keeps that behavior available while making the aerospace list an
explicit, reviewable configuration instead of scattering company names
through the polling code.
"""

from __future__ import annotations

import os


PROFILE_SWE_ML = "swe_ml"
PROFILE_AEROSPACE = "aerospace"


# This is the initial target manifest supplied for the aerospace/mechanical
# version.  A name in this set is a target even when its career board adapter
# has not been written yet; the adapter coverage report can then show the
# remaining implementation work without creating a failing fake adapter.
AEROSPACE_TARGET_COMPANIES = frozenset(
    {
        # Major aerospace and defense
        "Boeing",
        "Lockheed Martin",
        "Northrop Grumman",
        "RTX",
        "GE Aerospace",
        "General Atomics Aeronautical Systems",
        "General Dynamics",
        "Honeywell Aerospace",
        "L3Harris Technologies",
        "BAE Systems",
        "Textron",
        "Sierra Nevada Corporation",
        "Leidos",
        "Anduril Industries",
        "AeroVironment",
        "Shield AI",
        "Kratos Defense",
        "Moog",
        "Curtiss-Wright",
        "Parker Hannifin",
        # Space, launch, and spacecraft
        "SpaceX",
        "Blue Origin",
        "Rocket Lab",
        "Relativity Space",
        "Stoke Space",
        "Firefly Aerospace",
        "Axiom Space",
        "Astrobotic",
        "Intuitive Machines",
        "Planet Labs",
        "Millennium Space Systems",
        "Vast",
        "Redwire Space",
        "Maxar Space Systems",
        "Loft Orbital",
        "Varda Space Industries",
        "Impulse Space",
        "K2 Space",
        "True Anomaly",
        "Apex",
        "Honeybee Robotics",
        "AstroForge",
        "Gravitics",
        "Muon Space",
        "ispace",
        "Lunar Outpost",
        "Northwood Space",
        "GITAI",
        "SpinLaunch",
        "Astrolab",
        "Starpath",
        "Launcher",
        "Motiv Space Systems",
        # Advanced aircraft, autonomy, and eVTOL
        "Joby Aviation",
        "Archer Aviation",
        "Wisk Aero",
        "BETA Technologies",
        "Boom Supersonic",
        "Gulfstream Aerospace",
        "Embraer",
        "Piper Aircraft",
        "Cirrus Aircraft",
        "Zipline",
        "Field AI",
        # Advanced manufacturing and hardware
        "Machina Labs",
        "Karman Space & Defense",
        "Tesla",
        "Rivian",
        "Caterpillar",
        "John Deere",
        "Cummins",
        "Bosch",
        "Siemens",
        "Eaton",
        "Emerson",
        "Rockwell Automation",
        "Applied Materials",
        "ASML",
        "Lam Research",
        "Apple Hardware Engineering",
        # Engineering organizations
        "NASA",
        "NASA JPL",
        "The Aerospace Corporation",
        "Johns Hopkins Applied Physics Laboratory",
        "MIT Lincoln Laboratory",
        "MITRE",
        "Sandia National Laboratories",
        "Lawrence Livermore National Laboratory",
        "U.S. Air Force Research Laboratory",
        "Naval Research Laboratory",
        # Adjacent aerospace/defense companies already covered by the repo's
        # adapters and useful to keep in the initial pilot.
        "Astranis",
        "Epirus",
        "CACI International",
        "Mach Industries",
        "Skydio",
        "Hadrian",
        "Saronic",
    }
)


# Adapters present in the repository that match the supplied target manifest.
# This stays explicit so adapter coverage changes remain reviewable.
AEROSPACE_ADAPTER_COMPANIES = frozenset(
    {
        "Boeing",
        "Northrop Grumman",
        "RTX",
        "GE Aerospace",
        "General Atomics Aeronautical Systems",
        "BAE Systems",
        "Leidos",
        "Anduril Industries",
        "AeroVironment",
        "Shield AI",
        "SpaceX",
        "Blue Origin",
        "Rocket Lab",
        "Relativity Space",
        "Stoke Space",
        "Firefly Aerospace",
        "Vast",
        "Varda Space Industries",
        "Impulse Space",
        "K2 Space",
        "True Anomaly",
        "Apex",
        "The Aerospace Corporation",
        "Joby Aviation",
        "BETA Technologies",
        "Zipline",
        "Astranis",
        "Epirus",
        "CACI International",
        "Mach Industries",
        "Skydio",
        "Hadrian",
        "Saronic",
        "Planet Labs",
        "Archer Aviation",
        "Muon Space",
        "Machina Labs",
        "Gravitics",
        "Northwood Space",
        "Axiom Space",
        "Loft Orbital",
        "Wisk Aero",
        "Boom Supersonic",
        "Sierra Nevada Corporation",
        "Moog",
        "Curtiss-Wright",
        "Applied Materials",
        "Apple Hardware Engineering",
        "Caterpillar",
        "Astrolab",
        "Starpath",
        "ispace",
    }
)


def normalized_profile(value: str | None) -> str:
    """Normalize a profile name and fall back to the original behavior."""
    value = (value or PROFILE_SWE_ML).strip().lower().replace("-", "_")
    if value in {PROFILE_AEROSPACE, "aerospace_mechanical", "engineering"}:
        return PROFILE_AEROSPACE
    return PROFILE_SWE_ML


def role_title_filter(*, include_generic_engineering: bool = False):
    """Return the title predicate for the active profile.

    Existing adapters can therefore participate in the aerospace profile
    without changing the repository's original SWE/ML behavior when the
    profile is left at its default.
    """
    from .filters import (
        is_aerospace_mechanical_title,
        is_generic_engineering_internship_title,
        is_swe_ml_title,
    )

    if normalized_profile(os.environ.get("JOB_POLLER_PROFILE")) == PROFILE_AEROSPACE:
        if include_generic_engineering:
            return lambda title: (
                is_aerospace_mechanical_title(title)
                or is_generic_engineering_internship_title(title)
            )
        return is_aerospace_mechanical_title
    return is_swe_ml_title
