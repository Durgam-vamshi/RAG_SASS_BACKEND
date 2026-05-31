


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.chat import QueryRequest, QueryResponse
from app.services.retrieval import hybrid_search
from app.services.reranker import rerank
from app.services.llm import generate_answer

from app.services.chat_memory import (
    get_conversation,
    save_message,
    create_session_if_not_exists
)

from app.api.deps import get_current_user
from app.core.database import get_db

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


@router.post("/query", response_model=QueryResponse)
async def query(
    req: QueryRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    # Create session if missing
    create_session_if_not_exists(
        db,
        req.session_id,
        "default_user"
    )

    # Save user message
    save_message(
        db,
        req.session_id,
        "user",
        req.question
    )

    # Load conversation history
    history = get_conversation(
        db,
        req.session_id
    )

    # Retrieve documents
    candidates = await hybrid_search(
        req.question,
        user["org_id"],
        top_k=20
    )

    top_chunks = await rerank(
        req.question,
        candidates,
        top_n=5
    )

    # Generate answer with memory
    result = await generate_answer(
        req.question,
        top_chunks,
        history
    )

    # Save assistant response
    save_message(
        db,
        req.session_id,
        "assistant",
        result["answer"]
    )

    return result