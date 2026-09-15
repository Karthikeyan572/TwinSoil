from typing import List, Dict, Any

class EvidenceValidator:
    def validate_citations(
        self,
        claims: List[Dict[str, Any]],
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validates that every claim citing a source is supported by a chunk
        that was actually retrieved.
        """
        retrieved_sources = {c.get("source") for c in retrieved_chunks if c.get("source")}
        unsupported = []
        missing = []

        if not retrieved_chunks and claims:
            return {
                "valid": False,
                "missing_evidence": ["No evidence chunks were retrieved for the evaluated claims."],
                "unsupported_claims": [c.get("claim", "") for c in claims]
            }

        for c in claims:
            evidence_list = c.get("evidence", [])
            if not evidence_list:
                missing.append(f"Claim without evidence: {c.get('claim')}")
                continue
            for ev in evidence_list:
                src = ev.get("source")
                if src not in retrieved_sources:
                    unsupported.append(f"Cited source '{src}' was not found in retrieved chunks.")

        return {
            "valid": len(unsupported) == 0 and len(missing) == 0,
            "missing_evidence": missing,
            "unsupported_claims": unsupported
        }

evidence_validator = EvidenceValidator()
