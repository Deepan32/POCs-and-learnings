import logging
from typing import Tuple, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import httpx

from backend.app.config import settings
from backend.app.models.ai import AISetting, AIMode
from backend.app.ai.rag import KnowledgeRAG

logger = logging.getLogger("allstreak.ai.agent")

class AIAgentEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rag = KnowledgeRAG(db)

    async def get_settings(self, workspace_id: str) -> Optional[AISetting]:
        stmt = select(AISetting).where(AISetting.workspace_id == workspace_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def generate_response(
        self,
        workspace_id: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[str, float, bool]:
        """
        Returns:
            (response_text, confidence_score, should_handover)
        """
        ai_setting = await self.get_settings(workspace_id)
        if not ai_setting or ai_setting.mode == AIMode.OFF:
            return ("", 0.0, False)

        # Check explicit human request phrases
        human_keywords = ["human", "agent", "support person", "talk to someone", "representative", "real person"]
        if any(hk in user_message.lower() for hk in human_keywords):
            return (
                ai_setting.fallback_message or "Connecting you to our team specialist immediately.",
                1.0,
                True
            )

        # Search knowledge base
        kb_matches = await self.rag.search_knowledge(workspace_id, user_message, top_k=2)

        # Build context
        context_str = ""
        top_score = 0.0
        if kb_matches:
            top_score = kb_matches[0]["score"]
            context_str = "\n".join([f"- {item['title']}: {item['content']}" for item in kb_matches])

        # If OpenAI API Key is provided, call OpenAI
        if settings.OPENAI_API_KEY:
            try:
                system_prompt = (
                    f"You are {ai_setting.ai_name}, an automated assistant for {ai_setting.business_name}.\n"
                    f"Tone: {ai_setting.tone.value}.\n"
                    f"Business Description: {ai_setting.business_description or ''}\n"
                    f"Instructions: {ai_setting.instructions}\n"
                    f"Relevant Knowledge Base Context:\n{context_str}\n"
                    "If the answer is not in the context and cannot be answered reliably, say: [FALLBACK]"
                )
                
                messages = [{"role": "system", "content": system_prompt}]
                if conversation_history:
                    messages.extend(conversation_history[-4:])
                messages.append({"role": "user", "content": user_message})

                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                        json={
                            "model": settings.AI_DEFAULT_MODEL,
                            "messages": messages,
                            "max_tokens": ai_setting.max_tokens,
                            "temperature": 0.3
                        }
                    )
                    if resp.status_code == 200:
                        content = resp.json()["choices"][0]["message"]["content"].strip()
                        if "[FALLBACK]" in content or "FALLBACK" == content:
                            return (ai_setting.fallback_message, 0.4, ai_setting.auto_handover_on_fallback)
                        return (content, 0.95, False)
            except Exception as e:
                logger.warning(f"OpenAI call failed, falling back to local RAG: {e}")

        # Deterministic Intelligent RAG fallback
        if kb_matches and top_score >= 0.3:
            matched_doc = kb_matches[0]
            answer = matched_doc["content"]
            prefix = f"Hello! Regarding {matched_doc['title']}:\n" if not answer.startswith("Hello") else ""
            return (f"{prefix}{answer}", 0.85, False)

        # If confidence low
        if ai_setting.auto_handover_on_fallback:
            return (ai_setting.fallback_message, 0.3, True)

        return (
            f"Thank you for contacting {ai_setting.business_name}! How else may I assist you?",
            0.5,
            False
        )
