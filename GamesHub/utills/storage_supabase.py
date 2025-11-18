import boto3
import os
from datetime import datetime
from supabase import create_client

SUPABASE_URL = "https://ogasrlwtvqiilymwrmmk.storage.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

access_key = os.getenv("SUPABASE_ACCESS_KEY_ID")
secret_key = os.getenv("SUPABASE_SECRET_ACCESS_KEY")
endpoint_url = "https://ogasrlwtvqiilymwrmmk.storage.supabase.co/storage/v1/s3"
bucket_name = "GamesHubMedia"

s3 = boto3.client(
    "s3",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url=endpoint_url,
    region_name="ap-south-1",
)

def upload_file_to_supabase(file_obj, folder):

    original_name = file_obj.name
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename  = f"{timestamp}_{original_name}"

    object_key = f"{folder}/{filename}"

    file_obj.seek(0)
    s3.upload_fileobj(file_obj, bucket_name, object_key)

    return f"{endpoint_url}/{bucket_name}/{object_key}"

def delete_from_supabase(object_key):
    
    s3.delete_object(Bucket="GamesHubMedia", Key=object_key)

    return None

