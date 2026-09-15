import json
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy.orm import Session
from backend.app.database.database import SessionLocal
from backend.app.database.models import KnowledgeChunkModel
from backend.app.rag.embeddings import embedding_service

logger = logging.getLogger(__name__)

class VectorStore:
    def add_chunks(self, chunks: List[Dict[str, Any]]):
        db: Session = SessionLocal()
        try:
            texts = [c["content"] for c in chunks]
            embeddings = embedding_service.embed_documents(texts)
            
            for chunk_data, emb in zip(chunks, embeddings):
                existing = db.query(KnowledgeChunkModel).filter_by(
                    source=chunk_data["source"],
                    page=chunk_data.get("page"),
                    parameter=chunk_data.get("parameter")
                ).first()
                
                if existing:
                    existing.content = chunk_data["content"]
                    existing.title = chunk_data.get("title")
                    existing.organization = chunk_data.get("organization")
                    existing.section = chunk_data.get("section")
                    existing.topic = chunk_data.get("topic")
                    existing.document_type = chunk_data.get("document_type", "agricultural_reference")
                    existing.embedding = emb
                else:
                    db_chunk = KnowledgeChunkModel(
                        content=chunk_data["content"],
                        source=chunk_data["source"],
                        title=chunk_data.get("title"),
                        organization=chunk_data.get("organization"),
                        page=chunk_data.get("page"),
                        section=chunk_data.get("section"),
                        parameter=chunk_data.get("parameter"),
                        topic=chunk_data.get("topic"),
                        crop=chunk_data.get("crop"),
                        soil_type=chunk_data.get("soil_type"),
                        region=chunk_data.get("region"),
                        year=chunk_data.get("year"),
                        document_type=chunk_data.get("document_type", "agricultural_reference"),
                        embedding=emb
                    )
                    db.add(db_chunk)
            db.commit()
            logger.info(f"Successfully added/updated {len(chunks)} knowledge chunks in vector store.")
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding chunks to vector store: {e}")
            raise
        finally:
            db.close()

    def search(
        self,
        query: str,
        parameter_filter: Optional[str] = None,
        top_k: int = 3,
        threshold: float = 0.35
    ) -> List[Dict[str, Any]]:
        db: Session = SessionLocal()
        try:
            query_emb = np.array(embedding_service.embed_query(query), dtype=np.float32)
            query_norm = np.linalg.norm(query_emb)
            if query_norm > 0:
                query_emb = query_emb / query_norm

            db_query = db.query(KnowledgeChunkModel)
            all_chunks = db_query.all()
            if not all_chunks:
                return []

            scored_chunks = []
            for chunk in all_chunks:
                # Parameter filter boost or direct match
                param_match_boost = 0.0
                if parameter_filter and chunk.parameter:
                    if chunk.parameter.lower() == parameter_filter.lower():
                        param_match_boost = 0.25

                if not chunk.embedding:
                    continue

                chunk_emb = np.array(chunk.embedding, dtype=np.float32)
                chunk_norm = np.linalg.norm(chunk_emb)
                if chunk_norm > 0:
                    chunk_emb = chunk_emb / chunk_norm
                    cosine_sim = float(np.dot(query_emb, chunk_emb))
                else:
                    cosine_sim = 0.0

                final_score = cosine_sim + param_match_boost

                scored_chunks.append({
                    "id": chunk.id,
                    "content": chunk.content,
                    "source": chunk.source,
                    "title": chunk.title,
                    "organization": chunk.organization,
                    "page": chunk.page,
                    "section": chunk.section,
                    "parameter": chunk.parameter,
                    "score": round(final_score, 4),
                    "relevance": "HIGH" if final_score >= 0.6 else "MEDIUM"
                })

            # Sort by score descending
            scored_chunks.sort(key=lambda x: x["score"], reverse=True)
            filtered = [c for c in scored_chunks if c["score"] >= threshold]
            return filtered[:top_k]
        finally:
            db.close()

vector_store = VectorStore()
