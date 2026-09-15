import re
from typing import List, Optional, Dict, Any
from backend.app.extraction.soil_schema import (
    SoilParameter, SoilProfile, normalize_parameter_name, CANONICAL_PARAMETERS
)
from backend.app.validation.numerical_validator import validate_soil_profile_numerics

class ParameterExtractor:
    def extract_from_parsed(self, parsed_data: Dict[str, Any]) -> SoilProfile:
        raw_text = parsed_data.get("raw_text", "")
        tables = parsed_data.get("tables", [])
        
        parameters_map: Dict[str, SoilParameter] = {}
        sample_id = "Sample Report"
        crop_code = None

        # Look for Sample ID and Crop code in text
        for line in raw_text.split("\n"):
            line_str = line.strip()
            if "Sample ID" in line_str or "Sample:" in line_str:
                match = re.search(r"Sample(?:\s*ID)?[:\s\-]+([A-Za-z0-9_\s\-]+)", line_str, re.IGNORECASE)
                if match:
                    sample_id = match.group(1).strip()
            if "Crop" in line_str or "Target Crop" in line_str:
                match = re.search(r"Crop(?:\s*Code)?[:\s\-]+([A-Za-z0-9_\s\-/]+)", line_str, re.IGNORECASE)
                if match:
                    crop_code = match.group(1).strip()

        # 1. First extract from tables
        for table in tables:
            rows = table.get("rows", [])
            for row in rows:
                if len(row) >= 2:
                    self._parse_row(row, parameters_map)

        # 2. Extract from raw lines
        for line in raw_text.split("\n"):
            line_str = line.strip()
            if not line_str:
                continue
            # Check pipe delimited
            if "|" in line_str:
                parts = [p.strip() for p in line_str.split("|") if p.strip()]
                if len(parts) >= 2:
                    self._parse_row(parts, parameters_map)
                    continue

            # Check colon or tab delimited
            parts = [p.strip() for p in re.split(r"[:\t]+", line_str) if p.strip()]
            if len(parts) >= 2:
                self._parse_row(parts, parameters_map)

        profile = SoilProfile(
            sample_id=sample_id,
            crop_code=crop_code,
            parameters=list(parameters_map.values())
        )

        # Apply deterministic numerical validation
        return validate_soil_profile_numerics(profile)

    def _parse_row(self, cells: List[str], parameters_map: Dict[str, SoilParameter]):
        first_cell = cells[0].strip()
        canonical_name = normalize_parameter_name(first_cell)
        if not canonical_name:
            return

        # Do not overwrite if already found unless new has more data
        value_str = cells[1].strip() if len(cells) > 1 else ""
        lab_range_str = cells[2].strip() if len(cells) > 2 else ""
        lab_status_str = cells[3].strip() if len(cells) > 3 else ""

        val, unit = self._parse_value_and_unit(value_str)
        ref_min, ref_max, ref_text = self._parse_reference_range(lab_range_str)
        
        # If cells had only 2-3 items, check if range/status are in value_str
        if lab_status_str == "" and len(cells) > 2:
            # Maybe cell 2 is status or range
            if any(term in cells[2].upper() for term in ["OPTIMUM", "DEFICIENT", "HIGH", "LOW", "SAFE"]):
                lab_status_str = cells[2].strip()

        param = SoilParameter(
            name=canonical_name,
            value=val,
            unit=unit,
            reference_min=ref_min,
            reference_max=ref_max,
            reference_text=ref_text if ref_text else None,
            lab_status=lab_status_str if lab_status_str and lab_status_str != "—" else None,
            source_page=1
        )

        parameters_map[canonical_name] = param

    def _parse_value_and_unit(self, text: str) -> tuple[Optional[float], Optional[str]]:
        if not text or text == "—" or text == "-":
            return None, None
        
        match = re.search(r"([0-9]+\.?[0-9]*)\s*([a-zA-Z/%]+(?:\s*[0-9]+[a-zA-Z]*)?)?", text)
        if match:
            try:
                num = float(match.group(1))
                unit = match.group(2).strip() if match.group(2) else None
                return num, unit
            except ValueError:
                pass
        return None, None

    def _parse_reference_range(self, text: str) -> tuple[Optional[float], Optional[float], Optional[str]]:
        if not text or text == "—" or text == "-":
            return None, None, None

        ref_text = text.strip()
        # Pattern: min - max or min–max
        range_match = re.search(r"([0-9]+\.?[0-9]*)\s*[-–—to]+\s*([0-9]+\.?[0-9]*)", ref_text)
        if range_match:
            try:
                rmin = float(range_match.group(1))
                rmax = float(range_match.group(2))
                return rmin, rmax, ref_text
            except ValueError:
                pass

        # Pattern: > X
        gt_match = re.search(r">\s*([0-9]+\.?[0-9]*)", ref_text)
        if gt_match:
            try:
                return float(gt_match.group(1)), None, ref_text
            except ValueError:
                pass

        # Pattern: < X
        lt_match = re.search(r"<\s*([0-9]+\.?[0-9]*)", ref_text)
        if lt_match:
            try:
                return None, float(lt_match.group(1)), ref_text
            except ValueError:
                pass

        return None, None, ref_text

parameter_extractor = ParameterExtractor()
