import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.embeddings import _client
from app.retrieval import retrieve_chunks

TOOLS=[
    {
        "type": "function",
        "function": {
            "name":"search_chunks",
            "description": "Search the user's policy document for a given year.",
            "parameters":{
                "type":"object",
                "properties":{
                    "query":{"type":"string","description":"search query"},
                    "year":{"type":"integer","description":"policy year, e.g. 2026"}
                },
                "required":["query","year"]
            }
        }
    }
]

SYSTEM="""You answer questions about the user's banking policy document.
Use the search_chunks tool before answering. Search ONLY the year the user 
names, or the stated default year if none. Never search other years.
If a search returns policy text, answer from it. Quote numbers exactly."""

async def run_agent(db: AsyncSession, question: str, user_id: str, year_hint: int) -> str:
    messages=[
        {"role":"system","content":SYSTEM},
        {"role":"user","content":f"(default year if unspecified: {year_hint})\n{question}"}
    ]

    for _ in range(5):
        resp = await _client.chat.completions.create(
            model=settings.answer_model,
            messages=messages,
            tools=TOOLS
        )
        msg=resp.choices[0].message

        if not msg.tool_calls:
            return msg.content or ""

        messages.append(msg)

        for call in msg.tool_calls:
            args=json.loads(call.function.arguments)

            if call.function.name =="search_chunks":
                hits=await retrieve_chunks(
                    db, args["query"], user_id, args["year"]
                )
                result="\n---\n".join(
                    f"[year {c.year} page {c.page}] {c.text}" for c, _ in hits
                ) or "no results"
            else:
                result=f"unknown tool {call.function.name}"

            messages.append(
                {
                    "role":"tool",
                    "tool_call_id":call.id,
                    "content":result
                }
            )
    return "agent execeeded max steps"
