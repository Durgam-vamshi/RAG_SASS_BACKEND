
import uuid
import tempfile
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

from app.core.config import settings
from app.models.document import Document


# Free local embedding model
embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# qdrant = QdrantClient(url=settings.QDRANT_URL)
qdrant = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY
)

def ensure_collection():
    existing = [c.name for c in qdrant.get_collections().collections]

    if settings.QDRANT_COLLECTION not in existing:
        qdrant.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=384,  # all-MiniLM-L6-v2 output dimension
                distance=Distance.COSINE
            )
        )


async def ingest_document(
    contents: bytes,
    filename: str,
    doc_id: str,
    org_id: str,
    db
):
    ensure_collection()

    suffix = ".pdf" if filename.lower().endswith(".pdf") else ".txt"

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        if filename.lower().endswith(".pdf"):
            loader = PyPDFLoader(tmp_path)
        else:
            loader = TextLoader(tmp_path)

        pages = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=60
        )

        chunks = splitter.split_documents(pages)

        texts = [chunk.page_content for chunk in chunks]

        vectors = embeddings_model.embed_documents(texts)

        points = []

        for i, vector in enumerate(vectors):
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "text": texts[i],
                        "doc_id": doc_id,
                        "org_id": org_id,
                        "filename": filename,
                        "page": chunks[i].metadata.get("page", 0)
                    }
                )
            )

        qdrant.upsert(
            collection_name=settings.QDRANT_COLLECTION,
            points=points
        )

        doc = db.query(Document).filter(
            Document.id == doc_id
        ).first()

        if doc:
            doc.status = "ready"
            doc.chunk_count = len(chunks)
            db.commit()

    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)













