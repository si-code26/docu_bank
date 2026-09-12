"""Smoke tests: proving worker test setup is working"""

def test_sanity() -> None:
    assert 1 + 1 == 2

def test_boto3_importable() -> None:
    import boto3  # noqa: F401