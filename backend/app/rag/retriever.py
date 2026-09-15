import logging
from typing import List, Dict, Any, Optional
from backend.app.rag.vector_store import vector_store
from backend.app.config import settings

logger = logging.getLogger(__name__)

class ParameterRetriever:
    def retrieve_for_parameter(
        self,
        parameter_name: str,
        value: Optional[float] = None,
        unit: Optional[str] = None,
        status: Optional[str] = None,
        attempt: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Generates a parameter-specific query, searches vector store,
        evaluates relevance, and supports query refinement on retries.
        """
        # Formulate query dynamically based on attempt
        if attempt == 1:
            val_desc = f"{value} {unit}" if (value is not None and unit) else (f"{value}" if value is not None else "")
            status_desc = f"status {status}" if status else "agronomic optimum"
            query = f"Soil {parameter_name} {val_desc} {status_desc} nutrient sufficiency and crop impact"
            top_k = 3
        elif attempt == 2:
            # Query refinement: expand agronomic terminology
            query = f"Agricultural soil fertility interpretation for {parameter_name} deficiency toxicity and optimum range"
            top_k = 4
        else:
            # Broader retrieval on final attempt
            query = f"{parameter_name} soil testing extension recommendations"
            top_k = 5

        logger.info(f"Retrieval attempt {attempt} for parameter '{parameter_name}' with query: '{query}'")
        
        chunks = vector_store.search(
            query=query,
            parameter_filter=parameter_name,
            top_k=top_k,
            threshold=settings.RELEVANCE_THRESHOLD
        )
        
        # If no chunks met high threshold on attempt 1, widen slightly
        if not chunks and attempt < settings.MAX_RETRIES:
            logger.info(f"Weak evidence for {parameter_name} on attempt {attempt}. Triggering retry with query refinement.")
            return self.retrieve_for_parameter(
                parameter_name=parameter_name,
                value=value,
                unit=unit,
                status=status,
                attempt=attempt + 1
            )
            
        return chunks

parameter_retriever = ParameterRetriever()
