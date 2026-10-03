
import boto3

from app.config import settings


def get_s3_client():
    kwargs = {"region_name": "us-east-1"}
    if settings.s3_endpoint:
        kwargs["endpoint_url"] = settings.s3_endpoint
        kwargs["aws_access_key_id"] = "test"
        kwargs["aws_secret_access_key"] = "test"
    return boto3.client("s3", **kwargs)

def download_pdf(s3_key:str) -> bytes:
    s3=get_s3_client()
    obj=s3.get_object(Bucket=settings.s3_bucket, Key=s3_key)
    return obj["Body"].read()