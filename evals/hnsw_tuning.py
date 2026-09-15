"""HNSW tuning experiment: plan flip, ef_search sweep."""

import random
import time
import uuid

import numpy as np
import psycopg

DSN = "postgresql://docubank:docubank@localhost:5432/docubank"
DIMS = 1536
N_FAKE = 10_000
TOP_K = 4

random.seed(42)
np.random.seed(42)


def seed(conn) -> None:
    """Insert fake documents + N_FAKE random unit-vector chunks."""
    doc_ids = {}
    for u in range(1, 11):
        for yr in (2025, 2026):
            did = str(uuid.uuid4())
            conn.execute(
                "INSERT INTO documents (id, user_id, filename, year, s3_key, created_at)"
                " VALUES (%s, %s, %s, %s, %s, now())",
                (did, f"user{u}", f"fake-{yr}.pdf", yr, f"user{u}/fake-{yr}.pdf"),
            )
            doc_ids[(u, yr)] = did

    vecs = np.random.rand(N_FAKE, DIMS).astype(np.float32)
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)

    rows = []
    for i in range(N_FAKE):
        u = random.randint(1, 10)
        yr = random.choice((2025, 2026))
        rows.append(
            (
                str(uuid.uuid4()),
                doc_ids[(u, yr)],
                f"user{u}",
                yr,
                1,
                f"synthetic chunk {i}",
                str(vecs[i].tolist()),
            )
        )
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO chunks (id, document_id, user_id, year, page, text, embedding)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s::vector)",
            rows,
        )
    conn.commit()
    n = conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
    print(f"seeded; chunks now: {n}")


def query_ids(conn, qvec, user_id, year):
    return {
        r[0]
        for r in conn.execute(
            "SELECT id FROM chunks WHERE user_id=%s AND year=%s"
            " ORDER BY embedding <=> %s::vector LIMIT %s",
            (user_id, year, qvec, TOP_K),
        )
    }


def exact_topk(conn, qvec, user_id, year):
    """Ground truth via forced sequential scan."""
    conn.execute("SET enable_indexscan = off")
    ids = query_ids(conn, qvec, user_id, year)
    conn.execute("SET enable_indexscan = on")
    return ids


def hnsw_topk(conn, qvec, user_id, year, ef):
    conn.execute(f"SET hnsw.ef_search = {ef}")
    t0 = time.perf_counter()
    ids = query_ids(conn, qvec, user_id, year)
    ms = (time.perf_counter() - t0) * 1000
    return ids, ms


def random_unit_vector():
    q = np.random.rand(DIMS)
    return str((q / np.linalg.norm(q)).tolist())


def main() -> None:
    conn = psycopg.connect(DSN, autocommit=True)

    ans = input(f"Seed {N_FAKE} fake chunks? [y/N] ")
    if ans.lower() == "y":
        seed(conn)

    print("\n=== EXPLAIN ANALYZE at current row count ===")
    for line in conn.execute(
        "EXPLAIN ANALYZE SELECT id FROM chunks WHERE user_id='user1' AND year=2026"
        " ORDER BY embedding <=> %s::vector LIMIT 4",
        (random_unit_vector(),),
    ):
        print(line[0])

    print("\n=== ef_search sweep (20 queries each) ===")
    print(f"{'ef':>5} {'recall@4':>9} {'p50 ms':>8} {'p95 ms':>8}")
    for ef in (10, 40, 100, 400):
        recalls, times = [], []
        for _ in range(20):
            q = random_unit_vector()
            truth = exact_topk(conn, q, "user1", 2026)
            got, ms = hnsw_topk(conn, q, "user1", 2026, ef)
            if truth:
                recalls.append(len(truth & got) / len(truth))
            times.append(ms)
        print(
            f"{ef:>5} {np.mean(recalls):>9.3f}"
            f" {np.percentile(times, 50):>8.2f} {np.percentile(times, 95):>8.2f}"
        )

    conn.close()


if __name__ == "__main__":
    main()