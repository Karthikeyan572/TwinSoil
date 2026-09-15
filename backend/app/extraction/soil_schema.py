from typing import Optional, List
from pydantic import BaseModel, Field

CANONICAL_PARAMETERS = [
    "pH", "CEC", "Organic Matter", "N", "P", "K", "Ca", "Mg", "S",
    "B", "Mn", "Zn", "Cu", "Fe", "Al", "Pb", "EC"
]

CANONICAL_NAME_MAP = {
    "ph": "pH",
    "soil ph": "pH",
    "soil_ph": "pH",
    "cec": "CEC",
    "cation exchange capacity": "CEC",
    "cation exchange capacity (cec)": "CEC",
    "om": "Organic Matter",
    "organic matter": "Organic Matter",
    "organic matter %": "Organic Matter",
    "organic matter percent": "Organic Matter",
    "organic carbon": "Organic Matter",
    "n": "N",
    "nitrogen": "N",
    "total n": "N",
    "nitrate": "N",
    "nitrate-n": "N",
    "available n": "N",
    "p": "P",
    "phosphorus": "P",
    "available p": "P",
    "phosphate": "P",
    "bray p": "P",
    "olsen p": "P",
    "mehlich 3 p": "P",
    "k": "K",
    "potassium": "K",
    "available k": "K",
    "ca": "Ca",
    "calcium": "Ca",
    "mg": "Mg",
    "magnesium": "Mg",
    "s": "S",
    "sulfur": "S",
    "sulphur": "S",
    "so4": "S",
    "b": "B",
    "boron": "B",
    "mn": "Mn",
    "manganese": "Mn",
    "zn": "Zn",
    "zinc": "Zn",
    "cu": "Cu",
    "copper": "Cu",
    "fe": "Fe",
    "iron": "Fe",
    "al": "Al",
    "aluminum": "Al",
    "aluminium": "Al",
    "pb": "Pb",
    "lead": "Pb",
    "ec": "EC",
    "electrical conductivity": "EC",
    "soluble salts": "EC"
}

def normalize_parameter_name(raw_name: str) -> Optional[str]:
    cleaned = raw_name.strip().lower()
    if cleaned in CANONICAL_NAME_MAP:
        return CANONICAL_NAME_MAP[cleaned]
    # Check for prefix or substring matches
    for key, canonical in CANONICAL_NAME_MAP.items():
        if cleaned == key or cleaned.startswith(f"{key} ") or cleaned.endswith(f" {key}"):
            return canonical
    return None

class SoilParameter(BaseModel):
    name: str  # canonical name, e.g. "pH"
    value: Optional[float] = None
    unit: Optional[str] = None
    reference_min: Optional[float] = None
    reference_max: Optional[float] = None
    reference_text: Optional[str] = None  # original lab-stated range text, verbatim
    lab_status: Optional[str] = None  # original lab-stated status, verbatim, if present
    computed_status: Optional[str] = None  # BELOW_OPTIMUM, WITHIN_RANGE, ABOVE_OPTIMUM
    source_page: Optional[int] = None

class SoilProfile(BaseModel):
    sample_id: str = "Unknown Sample"
    crop_code: Optional[str] = None
    parameters: List[SoilParameter] = Field(default_factory=list)

class Evidence(BaseModel):
    source: str
    page: Optional[int] = None
    text: str
    relevance: str = "HIGH"

class ParameterInterpretation(BaseModel):
    parameter_name: str
    what_it_is: str
    what_value_means: str
    why_it_matters: str
    evidence: List[Evidence] = Field(default_factory=list)
    confidence: str = "HIGH"
