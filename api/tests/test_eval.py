"""Eval suite: fact-correctness, tenant isolation, and year isolation for /ask.

Bypasses real Cognito auth via dependency override — these tests check
retrieval + answer correctness against known fixture data, not auth.
Requires local Postgres seeded with fixture docs (user1/2025, user1/2026,
user2/2026, user3/2026) and a real OPENAI_API_KEY (these call the LLM).
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.auth import get_current_user
from app.db import engine
from app.main import app


CASES = [
    {
        "name": "overdraft_fee_2025",
        "user_id": "user1",
        "question": "what is my overdraft fee",
        "year": 2025,
        "must_contain": ["1%"],
        "must_not_contain": ["2%"],
    },
    {
        "name": "overdraft_fee_2026",
        "user_id": "user1",
        "question": "what is my overdraft fee",
        "year": 2026,
        "must_contain": ["2%"],
        "must_not_contain": ["1%"],
    },
    {
        "name": "year_not_specified_defaults_to_latest",
        "user_id": "user1",
        "question": "what is my overdraft fee",
        "year": None,
        "must_contain": ["2%"],
        "must_not_contain": [],
    },
    {
        "name": "tenant_isolation_user1_maintenance_fee",
        "user_id": "user1",
        "question": "what is my monthly maintenance fee",
        "year": 2026,
        "must_contain": ["$9.00", "9"],
        "must_not_contain": ["$15.00", "$5.00"],
    },
    {
        "name": "tenant_isolation_user2_maintenance_fee",
        "user_id": "user2",
        "question": "what is my monthly maintenance fee",
        "year": 2026,
        "must_contain": ["$15.00"],
        "must_not_contain": ["$9.00", "$5.00"],
    },
    {
        "name": "tenant_isolation_user3_maintenance_fee",
        "user_id": "user3",
        "question": "what is my monthly maintenance fee",
        "year": 2026,
        "must_contain": ["$5.00"],
        "must_not_contain": ["$9.00", "$15.00"],
    },
    {
        "name": "no_doc_for_wrong_year",
        "user_id": "user1",
        "question": "what is my overdraft fee",
        "year": 2099,
        "expect_404": True,
    },
]

@pytest.fixture(autouse=True)
async def _dispose_engine_after_test():
    yield
    await engine.dispose()

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def override_user(user_id: str):
    async def _override():
        return user_id
    return _override


@pytest.mark.asyncio
@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
async def test_ask_eval(client, case):
    app.dependency_overrides[get_current_user] = override_user(case["user_id"])
    try:
        payload = {"question": case["question"]}
        if case.get("year") is not None:
            payload["year"] = case["year"]

        resp = await client.post("/ask", json=payload)

        if case.get("expect_404"):
            assert resp.status_code == 404, f"{case['name']}: expected 404, got {resp.status_code}"
            return

        assert resp.status_code == 200, f"{case['name']}: {resp.status_code} {resp.text}"
        answer = resp.json()["answer"].lower()

        for phrase in case.get("must_contain", []):
            assert phrase.lower() in answer, (
                f"{case['name']}: expected '{phrase}' in answer, got: {answer}"
            )
        for phrase in case.get("must_not_contain", []):
            assert phrase.lower() not in answer, (
                f"{case['name']}: found forbidden '{phrase}' in answer: {answer}"
            )
    finally:
        app.dependency_overrides.clear()