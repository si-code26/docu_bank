import boto3

S3_ENDPOINT = "http://localhost:4566"
BUCKET="docubank-uploads"

def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1"
    )

def upload_pdf(user_id: str, filename: str, content: bytes) -> str:
    key = f"{user_id}/{filename}"
    s3 = get_s3_client()
    s3.put_object(Bucket=BUCKET, Key=key, Body=content, ContentType="application/pdf")
    return key