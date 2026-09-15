from typing import Optional, Tuple
from backend.app.extraction.soil_schema import SoilParameter, SoilProfile

def compute_numerical_status(
    value: Optional[float],
    reference_min: Optional[float],
    reference_max: Optional[float]
) -> Optional[str]:
    """
    Deterministically computes categorical status based on value and reference ranges.
    Returns: 'BELOW_OPTIMUM', 'ABOVE_OPTIMUM', 'WITHIN_RANGE', or None if inputs insufficient.
    """
    if value is None:
        return None

    if reference_min is not None and reference_max is not None:
        if value < reference_min:
            return "BELOW_OPTIMUM"
        elif value > reference_max:
            return "ABOVE_OPTIMUM"
        else:
            return "WITHIN_RANGE"
    elif reference_min is not None:
        if value < reference_min:
            return "BELOW_OPTIMUM"
        else:
            return "WITHIN_RANGE"
    elif reference_max is not None:
        if value > reference_max:
            return "ABOVE_OPTIMUM"
        else:
            return "WITHIN_RANGE"

    return None

def validate_soil_profile_numerics(profile: SoilProfile) -> SoilProfile:
    """
    Validates all parameters in a profile deterministically and assigns computed_status
    while preserving original lab_status verbatim.
    """
    for param in profile.parameters:
        param.computed_status = compute_numerical_status(
            value=param.value,
            reference_min=param.reference_min,
            reference_max=param.reference_max
        )
    return profile
