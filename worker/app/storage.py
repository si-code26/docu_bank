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

def download_pdf(s3_key:str) -> bytes:
    s3=get_s3_client()
    obj=s3.get_object(Bucket=settings.s3_bucket, Key=s3_key)
    return obj["Body"].read()