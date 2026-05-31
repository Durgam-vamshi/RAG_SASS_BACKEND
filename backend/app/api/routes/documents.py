from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.document import Document
from app.services.ingestion import ingest_document
from app.api.deps import get_current_user

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_TYPES = [
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
]

@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF, TXT, DOCX allowed")

    doc = Document(filename=file.filename, org_id=user["org_id"])
    db.add(doc)
    db.commit()
    db.refresh(doc)

    contents = await file.read()
    await ingest_document(
        contents, file.filename, str(doc.id), user["org_id"], db
    )

    return {"document_id": str(doc.id), "filename": file.filename, "status": "processing"}

@router.get("/")
def list_documents(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    docs = db.query(Document).filter(Document.org_id == user["org_id"]).all()
    return docs