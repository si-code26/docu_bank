import boto3
import json

from app.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1"
    )

def upload_pdf(user_id: str, filename: str, content: bytes) -> str:
    key = f"{user_id}/{filename}"
    s3 = get_s3_client()
    s3.put_object(Bucket=settings.s3_bucket, Key=key, Body=content, ContentType="application/pdf")
    return key

def publish_ingest_job(document_id: str) -> None:
    sqs=boto3.client(
        "sqs",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1"
    )
    sqs.send_message(
        QueueUrl="http://localhost:4566/000000000000/docubank-ingest",
        MessageBody=json.dumps({"document_id":document_id})
    )