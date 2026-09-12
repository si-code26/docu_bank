"""Smoke tests: prove the test setup itself works."""

def test_sanity() -> None:
    assert 1 + 1 == 2

def test_fastapi_importable() -> None:
    import fastapi  # noqa: F401

    