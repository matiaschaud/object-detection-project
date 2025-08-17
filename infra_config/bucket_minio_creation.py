import boto3
import sys

# This script connects to a Minio S3 service and attempts to create a specified bucket.
# It takes the bucket name, AWS access key ID, and AWS secret access key as command-line arguments.

def create_minio_bucket(bucket_name, aws_access_key_id, aws_secret_access_key):
    """
    Connects to a Minio S3 service and attempts to create a specified bucket.

    Args:
        bucket_name (str): The name of the S3 bucket to create.
        aws_access_key_id (str): The access key ID for AWS/Minio.
        aws_secret_access_key (str): The secret access key for AWS/Minio.
    """
    print(f"Attempting to connect to Minio and create bucket: {bucket_name}")
    print(f"Using access key ID: {aws_access_key_id}")

    try:
        # Initialize the S3 client for Minio
        # The endpoint_url is hardcoded as per your original script.
        minio_client = boto3.client(
            's3',
            endpoint_url='http://minio-service.kubeflow.svc.cluster.local:9000',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

        # Attempt to create the bucket
        minio_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' created successfully or already exists.")

    except Exception as e:
        # This block catches any exception, often indicating the bucket already exists
        # or there was an issue with credentials/connection.
        print(f"An error occurred while trying to create bucket '{bucket_name}': {e}")
        # You might want to add more specific error handling here
        # based on the type of exception (e.g., if it's a Boto3 client error).

if __name__ == "__main__":
    # Check if the correct number of arguments are provided
    if len(sys.argv) != 4:
        print("Usage: python script_name.py <bucket_name> <aws_access_key_id> <aws_secret_access_key>")
        print("Example: python create_bucket.py my-new-bucket minio_user minio_password")
        sys.exit(1) # Exit with an error code

    # Retrieve arguments from the command line
    # sys.argv[0] is the script name itself
    # sys.argv[1] is bucket_name
    # sys.argv[2] is aws_access_key_id
    # sys.argv[3] is aws_secret_access_key
    bucket = sys.argv[1]
    access_key = sys.argv[2]
    secret_key = sys.argv[3]

    # Call the function with the provided arguments
    create_minio_bucket(bucket, access_key, secret_key)        