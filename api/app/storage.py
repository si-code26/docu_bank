import json

import boto3

from app.config import settings


def get_s3_client():
    kwargs = {"region_name": "us-east-1"}
    if settings.s3_endpoint:
        kwargs["endpoint_url"] = settings.s3_endpoint
        kwargs["aws_access_key_id"] = "test"
        kwargs["aws_secret_access_key"] = "test"
    return boto3.client("s3", **kwargs)

def upload_pdf(user_id: str, filename: str, content: bytes) -> str:
    key = f"{user_id}/{filename}"
    s3 = get_s3_client()
    s3.put_object(Bucket=settings.s3_bucket, Key=key, Body=content, ContentType="application/pdf")
    return key

def publish_ingest_job(document_id: str) -> None:
    kwargs = {"region_name": "us-east-1"}
    if settings.sqs_endpoint:
        kwargs["endpoint_url"] = settings.sqs_endpoint
        kwargs["aws_access_key_id"] = "test"
        kwargs["aws_secret_access_key"] = "test"
    sqs = boto3.client("sqs", **kwargs)
    sqs.send_message(
        QueueUrl=settings.ingest_queue_url,
        MessageBody=json.dumps({"document_id":document_id})
    )

