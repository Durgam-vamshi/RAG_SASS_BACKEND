


from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from rank_bm25 import BM25Okapi

from app.core.config import settings

# Local embeddings
embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

qdrant = QdrantClient(url=settings.QDRANT_URL)


async def hybrid_search(
    query: str,
    org_id: str,
    top_k: int = 20
) -> list:

    # =========================
    # VECTOR SEARCH
    # =========================

    query_vector = embeddings_model.embed_query(query)

    search_result = qdrant.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="org_id",
                    match=MatchValue(value=org_id)
                )
            ]
        ),
        limit=top_k
    )

    vector_results = search_result.points

    # =========================
    # BM25 SEARCH
    # =========================

    all_chunks, _ = qdrant.scroll(
        collection_name=settings.QDRANT_COLLECTION,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="org_id",
                    match=MatchValue(value=org_id)
                )
            ]
        ),
        limit=1000
    )

    if not all_chunks:
        return vector_results

    corpus = []

    for chunk in all_chunks:
        text = chunk.payload.get("text", "")
        corpus.append(text)

    tokenized_corpus = [
        doc.lower().split()
        for doc in corpus
    ]

    bm25 = BM25Okapi(tokenized_corpus)

    bm25_scores = bm25.get_scores(
        query.lower().split()
    )

    bm25_top_idx = sorted(
        range(len(bm25_scores)),
        key=lambda i: bm25_scores[i],
        reverse=True
    )[:top_k]

    bm25_results = [
        all_chunks[i]
        for i in bm25_top_idx
    ]

    # =========================
    # RECIPROCAL RANK FUSION
    # =========================

    k = 60
    scores = {}

    for rank, result in enumerate(vector_results):
        scores[result.id] = (
            scores.get(result.id, 0)
            + 1 / (k + rank + 1)
        )

    for rank, result in enumerate(bm25_results):
        scores[result.id] = (
            scores.get(result.id, 0)
            + 1 / (k + rank + 1)
        )

    all_results = {}

    for result in vector_results:
        all_results[result.id] = result

    for result in bm25_results:
        all_results[result.id] = result

    sorted_ids = sorted(
        scores.keys(),
        key=lambda x: scores[x],
        reverse=True
    )

    return [
        all_results[result_id]
        for result_id in sorted_ids[:top_k]
        if result_id in all_results
    ]
