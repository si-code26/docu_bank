import json

import boto3
import pymupdf
from app.chunking import chunk_text
from sqlalchemy import select

from app.db import SessionFactory
from app.embeddings import embed_texts
from app.models import Chunk, Document
from app.storage import download_pdf

QUEUE_URL="http://localhost:4566/000000000000/docubank-ingest"

def get_sqs_client():
    return boto3.client(
        "sqs", 
        endpoint_url="http://localhost:4566",
        aws_access_key_id="test", 
        aws_secret_access_key="test",
        region_name="us-east-1"
    )

async def process_message(body:dict) -> None:
    doc_id=body["document_id"]
    async with SessionFactory() as db:
        existing=await db.execute(select(Chunk).where(Chunk.document_id==doc_id).limit(1))
        if existing.first():
            print(f"Skip {doc_id}: already processed")
            return
        
        doc=(await db.execute(select(Document).where(Document.id==doc_id))).scalar_one()
        content=download_pdf(doc.s3_key)
        
        pdf=pymupdf.open(stream=content, filetype="pdf")
        for page_number, page in enumerate(pdf,start=1):
            page_text=page.get_text().strip()
            if not page_text:
                continue
            pieces=chunk_text(page_text)
            if not pieces:
                continue
            vectors=await embed_texts(pieces)
            for piece, vector in zip(pieces, vectors, strict=True):
                db.add(Chunk(
                    document_id=doc.id,
                    user_id=doc.user_id,
                    year=doc.year,
                    page=page_number,
                    text=piece,
                    embedding=vector
                ))

        pdf.close()
        await db.commit()
        print(f"processed {doc_id}")

async def poll_loop():
    sqs=get_sqs_client()
    print("working polling...")
    while True:
        resp = sqs.receive_message(QueueUrl=QUEUE_URL, MaxNumberOfMessages=1, WaitTimeSeconds=10)
        for msg in resp.get("Messages", []):
            body=json.loads(msg["Body"])
            await process_message(body)
            sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=msg["ReceiptHandle"])
