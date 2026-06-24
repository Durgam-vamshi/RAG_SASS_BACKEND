from sentence_transformers import CrossEncoder

reranker_model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

async def rerank(query: str, candidates: list, top_n: int = 5):
    if not candidates:
        return []

    pairs = [
        (query, c.payload["text"])
        for c in candidates
    ]

    scores = reranker_model.predict(pairs)

    ranked = sorted(
        zip(candidates, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [item[0] for item in ranked[:top_n]]
