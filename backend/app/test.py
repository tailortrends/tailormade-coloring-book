import boto3
from botocore.exceptions import ClientError
from app.config import get_settings

def test_r2():
    settings = get_settings()
    print(f"--- Testing R2 Connection ---")
    print(f"Bucket: {settings.r2_bucket_name}")
    
    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
    )

    try:
        # This is the exact call your health check makes
        s3.head_bucket(Bucket=settings.r2_bucket_name)
        print("✅ SUCCESS: Bucket is accessible!")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ FAILED: {error_code}")
        if error_code == "403":
            print("Check: Token permissions (Needs Read/Write).")
        elif error_code == "401" or error_code == "SignatureDoesNotMatch":
            print("Check: Secret Access Key is incorrect or has extra characters.")
        elif error_code == "404":
            print("Check: Bucket name is misspelled.")
    except Exception as e:
        print(f"❌ UNKNOWN ERROR: {e}")

if __name__ == "__main__":
    test_r2()