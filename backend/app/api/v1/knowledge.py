from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_workspace, RoleChecker
from backend.app.models.workspace import Workspace, RoleEnum
from backend.app.models.knowledge import KnowledgeBase, KnowledgeDocument, KnowledgeCategory
from backend.app.schemas.knowledge import (
    KnowledgeBaseCreate, KnowledgeBaseResponse,
    KnowledgeDocumentCreate, KnowledgeDocumentResponse,
    RAGQueryRequest, RAGQueryResponse
)
from backend.app.ai.rag import KnowledgeRAG

router = APIRouter()

@router.get("", response_model=List[KnowledgeBaseResponse])
async def list_knowledge_bases(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(KnowledgeBase)
        .options(selectinload(KnowledgeBase.documents))
        .where(KnowledgeBase.workspace_id == workspace.id)
    )
    res = await db.execute(stmt)
    kbs = res.scalars().all()
    output = []
    for kb in kbs:
        docs = [KnowledgeDocumentResponse.model_validate(d) for d in kb.documents]
        kbr = KnowledgeBaseResponse(
            id=kb.id,
            workspace_id=kb.workspace_id,
            name=kb.name,
            description=kb.description,
            is_active=kb.is_active,
            created_at=kb.created_at,
            documents=docs
        )
        output.append(kbr)
    return output

@router.post("", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(
    payload: KnowledgeBaseCreate,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    kb = KnowledgeBase(
        workspace_id=workspace.id,
        name=payload.name,
        description=payload.description
    )
    db.add(kb)
    await db.commit()
    await db.refresh(kb)
    return KnowledgeBaseResponse(
        id=kb.id,
        workspace_id=kb.workspace_id,
        name=kb.name,
        description=kb.description,
        is_active=kb.is_active,
        created_at=kb.created_at,
        documents=[]
    )

@router.post("/{id}/documents", response_model=KnowledgeDocumentResponse)
async def add_document(
    id: str,
    payload: KnowledgeDocumentCreate,
    workspace: Workspace = Depends(get_current_workspace),
    _=Depends(RoleChecker([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(KnowledgeBase).where(KnowledgeBase.id == id, KnowledgeBase.workspace_id == workspace.id)
    res = await db.execute(stmt)
    kb = res.scalars().first()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    doc = KnowledgeDocument(
        knowledge_base_id=kb.id,
        title=payload.title,
        category=payload.category,
        question=payload.question,
        answer_or_content=payload.answer_or_content,
        keywords=payload.keywords,
        is_active=payload.is_active if payload.is_active is not None else True
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return KnowledgeDocumentResponse.model_validate(doc)

@router.post("/query-test", response_model=RAGQueryResponse)
async def query_knowledge_rag(
    payload: RAGQueryRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    rag = KnowledgeRAG(db)
    matches = await rag.search_knowledge(workspace.id, payload.query, top_k=2)
    if matches:
        top = matches[0]
        return RAGQueryResponse(
            matched=True,
            confidence=top["score"],
            answer=top["content"],
            source_documents=[m["title"] for m in matches]
        )
    return RAGQueryResponse(
        matched=False,
        confidence=0.0,
        answer="No matching knowledge found for this query in the business knowledge base.",
        source_documents=[]
    )
