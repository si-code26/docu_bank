"""Seed script for CI: creates schema + inserts fixture data test_eval.py depends on.

Run once per fresh CI Postgres container, before pytest. Assumes a FRESH
database — exactly what CI's service container gives you on every run.
"""

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings
from app.embeddings import embed_texts
from app.models import Base, Chunk, Document

FIXTURES = [
    {
        "user_id": "user1",
        "year": 2025,
        "filename": "faq-2025.pdf",
        "text": (
            "DocuBank Policy FAQ - 2025\n"
            "Account holder: user1\n"
            "Effective year: 2025\n"
            "Overdraft fee: 1% of the overdrawn amount\n"
            "Monthly maintenance fee: $9.00\n"
            "ATM withdrawal limit: $300 per day\n"
            "Wire transfer fee: $17.00 per transfer.\n"
            "Contact support for questions about your account"
        ),
    },
    {
        "user_id": "user1",
        "year": 2026,
        "filename": "faq-2026.pdf",
        "text": (
            "DocuBank Policy FAQ - 2026\n"
            "Account holder: user1\n"
            "Effective year: 2026\n"
            "Overdraft fee: 2% of the overdrawn amount\n"
            "Monthly maintenance fee: $9.00\n"
            "ATM withdrawal limit: $300 per day\n"
            "Wire transfer fee: $17.00 per transfer.\n"
            "Contact support for questions about your account"
        ),
    },
    {
        "user_id": "user2",
        "year": 2026,
        "filename": "faq-2026.pdf",
        "text": (
            "DocuBank Policy FAQ - 2026\n"
            "Account holder: user2\n"
            "Effective year: 2026\n"
            "Overdraft fee: 2% of the overdrawn amount\n"
            "Monthly maintenance fee: $15.00\n"
            "ATM withdrawal limit: $1000 per day\n"
            "Wire transfer fee: $27.00 per transfer.\n"
            "Contact support for questions about your account"
        ),
    },
    {
        "user_id": "user3",
        "year": 2026,
        "filename": "faq-2026.pdf",
        "text": (
            "DocuBank Policy FAQ - 2026\n"
            "Account holder: user3\n"
            "Effective year: 2026\n"
            "Overdraft fee: 2% of the overdrawn amount\n"
            "Monthly maintenance fee: $5.00\n"
            "ATM withdrawal limit: $300 per day\n"
            "Wire transfer fee: $12.00 per transfer.\n"
            "Contact support for questions about your account"
        ),
    },
]


async def main() -> None:
    engine = create_async_engine(settings.database_url)

    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

    texts = [f["text"] for f in FIXTURES]
    vectors = await embed_texts(texts)

    SessionFactory = async_sessionmaker(engine, expire_on_commit=False)
    async with SessionFactory() as session:
        for fixture, vector in zip(FIXTURES, vectors, strict=True):
            doc = Document(
                user_id=fixture["user_id"],
                filename=fixture["filename"],
                year=fixture["year"],
                s3_key=f"seed/{fixture['user_id']}/{fixture['filename']}",
            )
            chunk = Chunk(
                document=doc,
                user_id=fixture["user_id"],
                year=fixture["year"],
                page=1,
                text=fixture["text"],
                embedding=vector,
            )
            session.add(doc)
            session.add(chunk)
        await session.commit()

    await engine.dispose()
    print(f"Seeded {len(FIXTURES)} fixture documents.")


if __name__ == "__main__":
    asyncio.run(main())