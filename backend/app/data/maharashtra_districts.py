"""Canonical Maharashtra district names used to disambiguate map searches."""

MAHARASHTRA_DISTRICTS = frozenset(
    {
        "Ahilyanagar", "Akola", "Amravati", "Beed", "Bhandara", "Buldhana",
        "Chandrapur", "Chhatrapati Sambhajinagar", "Dharashiv", "Dhule",
        "Gadchiroli", "Gondia", "Hingoli", "Jalgaon", "Jalna", "Kolhapur",
        "Latur", "Mumbai City", "Mumbai Suburban", "Nagpur", "Nanded",
        "Nandurbar", "Nashik", "Palghar", "Parbhani", "Pune", "Raigad",
        "Ratnagiri", "Sangli", "Satara", "Sindhudurg", "Solapur", "Thane",
        "Wardha", "Washim", "Yavatmal",
    }
)

# The supplied district map uses former names; keep them valid search inputs.
DISTRICT_ALIASES = {
    "Ahmednagar": "Ahilyanagar",
    "Aurangabad": "Chhatrapati Sambhajinagar",
    "Osmanabad": "Dharashiv",
}


def normalise_scope(value: str) -> str:
    return " ".join(value.lower().replace(" district", "").split())


_DISTRICTS_BY_NORMALISED_NAME = {
    normalise_scope(name): name for name in MAHARASHTRA_DISTRICTS
} | {
    normalise_scope(alias): canonical for alias, canonical in DISTRICT_ALIASES.items()
}


def canonical_maharashtra_district(value: str) -> str | None:
    return _DISTRICTS_BY_NORMALISED_NAME.get(normalise_scope(value))
