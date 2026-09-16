import re
from typing import List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.models.knowledge import KnowledgeBase, KnowledgeDocument

class KnowledgeRAG:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_knowledge(self, workspace_id: str, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves relevant knowledge base documents for workspace based on token matching and keyword scoring.
        """
        stmt = (
            select(KnowledgeDocument)
            .join(KnowledgeBase, KnowledgeBase.id == KnowledgeDocument.knowledge_base_id)
            .where(
                KnowledgeBase.workspace_id == workspace_id,
                KnowledgeBase.is_active == True,
                KnowledgeDocument.is_active == True
            )
        )
        res = await self.db.execute(stmt)
        docs = res.scalars().all()

        if not docs:
            return []

        query_tokens = set(re.findall(r'\w+', query.lower()))
        scored_docs: List[Tuple[float, KnowledgeDocument]] = []

        for doc in docs:
            doc_text = f"{doc.title} {doc.question or ''} {doc.answer_or_content} {doc.keywords or ''}".lower()
            doc_tokens = set(re.findall(r'\w+', doc_text))
            
            overlap = query_tokens.intersection(doc_tokens)
            if overlap:
                # Score based on overlap ratio and keyword match
                score = len(overlap) / (len(query_tokens) + 1)
                # Boost if in question or keywords
                if doc.keywords and any(kw.strip().lower() in query.lower() for kw in doc.keywords.split(",")):
                    score += 0.5
                if doc.question and any(qt in doc.question.lower() for qt in query_tokens):
                    score += 0.3
                scored_docs.append((score, doc))

        # Sort by score descending
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, doc in scored_docs[:top_k]:
            results.append({
                "id": doc.id,
                "title": doc.title,
                "category": doc.category.value,
                "question": doc.question,
                "content": doc.answer_or_content,
                "score": min(round(score, 2), 1.0)
            })

        return results
