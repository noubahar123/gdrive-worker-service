# app/storage.py
import os
import boto3
from botocore.client import Config
from urllib.parse import quote_plus

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
AWS_S3_ENDPOINT = os.getenv("AWS_S3_ENDPOINT")  # optional for DO Spaces, R2, etc.

if not (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_S3_BUCKET):
    raise RuntimeError("AWS S3 env vars not fully set (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET).")


def get_s3_client():
    if AWS_S3_ENDPOINT:
        return boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            endpoint_url=AWS_S3_ENDPOINT,
            region_name=AWS_REGION,
            config=Config(signature_version="s3v4"),
        )
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )


def upload_bytes_to_s3(key: str, data: bytes, content_type: str | None = None, acl: str = "public-read") -> str:
    """
    Upload bytes to S3 and return a public URL.
    key: object key in bucket, e.g. 'imports/{folder_id}/{filename}'
    """
    client = get_s3_client()
    kwargs = {"Bucket": AWS_S3_BUCKET, "Key": key, "Body": data}
    if content_type:
        kwargs["ContentType"] = content_type

    # Try with put_object (most compatible)
    client.put_object(**kwargs)

    # Construct a URL (works for AWS + many S3-compatible endpoints)
    if AWS_S3_ENDPOINT:
        endpoint = AWS_S3_ENDPOINT.rstrip("/")
        return f"{endpoint}/{AWS_S3_BUCKET}/{quote_plus(key)}"
    else:
        return f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{quote_plus(key)}"
