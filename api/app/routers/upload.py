import re

import pymupdf
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.storage import publish_ingest_job
from app.chunking import chunk_text
from app.db import get_db
from app.embeddings import embed_texts
from app.models import Chunk, Document
from app.schemas import UploadResponse
from app.storage import upload_pdf

router = APIRouter()
YEAR_RE=re.compile(r"(20\d{2})")

@router.post("/upload", response_model=UploadResponse)
async def upload(
    file: UploadFile,
    user_id: str=Form(...),
    db: AsyncSession=Depends(get_db)
) -> UploadResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="only PDF files accepted")

    match=YEAR_RE.search(file.filename)
    if not match:
        raise HTTPException(
            status_code= 400,
            detail="filename must contain year in format 20XX"
        )

    year=int(match.group(1))
    content=await file.read()
    s3_key=upload_pdf(user_id,file.filename,content)
    doc=Document(user_id=user_id, filename=file.filename, year=year,s3_key=s3_key)
    db.add(doc)
    await db.flush()
    
    pdf = pymupdf.open(stream=content,filetype="pdf")
    chunk_count=0
    for page_number, page in enumerate(pdf, start=1):
        page_text = page.get_text().strip()
        if not page_text:
            continue
        pieces=chunk_text(page_text)
        if not pieces:
            continue
        vectors=await embed_texts(pieces)
        for piece,vector in zip(pieces,vectors,strict=True):
            db.add(
                Chunk(
                    document_id=doc.id,
                    user_id=user_id,
                    year=year,
                    page=page_number,
                    text=piece,
                    embedding=vector
                )
            )
            chunk_count += 1
    pdf.close()

    publish_ingest_job(str(doc.id))
    await db.commit()

    return UploadResponse(
        document_id=doc.id,
        filename=file.filename,
        year=year,
        chunk_count=0
    )
    