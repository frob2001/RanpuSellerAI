import os
import json
from google.cloud import storage
from google.oauth2 import service_account

class GoogleCloudStorageConfig:
    def __init__(self):
        """
        Initializes the Google Cloud Storage client using environment variables stored in .env.
        """
        # Reconstruct the service account JSON from environment variables
        service_account_info = {
            "type": os.getenv("GOOGLE_TYPE"),
            "project_id": os.getenv("GOOGLE_PROJECT_ID"),
            "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
            "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
            "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_X509_CERT_URL"),
            "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
        }

        # Initialize the Google Cloud Storage client using the reconstructed service account info
        credentials = service_account.Credentials.from_service_account_info(service_account_info)
        self.storage_client = storage.Client(credentials=credentials, project=service_account_info["project_id"])

    def get_bucket(self, bucket_name):
        """
        Retrieve the specified bucket object.

        :param bucket_name: Name of the Google Cloud Storage bucket.
        :return: A Bucket object.
        """
        try:
            bucket = self.storage_client.bucket(bucket_name)
            return bucket
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve bucket '{bucket_name}': {e}")
