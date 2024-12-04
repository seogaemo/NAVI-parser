import os
import boto3
from botocore.client import Config


class S3Uploader:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
            endpoint_url=os.getenv("S3_ENDPOINT_URL"),
            region_name="auto",
            config=Config(signature_version="s3v4"),
        )

        self.bucketName = "road"

    def uploadFrame(self, buffer, key):
        try:
            # 프레임 데이터를 S3에 업로드
            self.s3_client.upload_fileobj(buffer, self.bucketName, key)
        except Exception as e:
            print(f"Failed to upload {key}: {e}")
