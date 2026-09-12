import re
import pymupdf
from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import UploadResponse
from app.storage import upload_pdf
from app.models import Chunk, Document
from app.db import get_db

router = APIRouter()
YEAR_RE=re.compile(r"(20\d{2})")

@router.post("/upload", response_model=UploadResponse)
async def upload(
    file: UploadFile,
    user_id: str=Form(...),
    db: AsyncSession=Depends(get_db)
) -> UploadResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status=400, detail="only PDF files accepted")

    match=YEAR_RE.search(file.filename)
    if not match:
        raise HTTPException(
            status_code= 400,
            detail="filename must contain year in format 20XX"
        )

    year=int(match.group(1))
    content=await file.read()
    s3_key=upload_pdf(user_id,file.filename,content)
    doc=Document(user_id=user_id, filename=file.filename, year=year)
    db.add(doc)
    await db.flush()
    
    pdf = pymupdf.open(stream=content,filetype="pdf")
    chunk_count=0
    for page_number, page in enumerate(pdf, start=1):
        text = page.get_text().strip()
        if not text:
            continue
        db.add(
            Chunk(
                document_id=doc.id,
                user_id=user_id,
                year=year,
                page=page_number,
                text=text
            )
        )
        chunk_count += 1
    pdf.close()

    await db.commit()

    return UploadResponse(
        document_id=doc.id,
        filename=file.filename,
        year=year,
        chunk_count=chunk_count
    )
    