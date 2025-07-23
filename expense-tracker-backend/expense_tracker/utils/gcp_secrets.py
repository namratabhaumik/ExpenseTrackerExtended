import os
from google.cloud import secretmanager

# Initialize the Secret Manager client
client = secretmanager.SecretManagerServiceClient()

# Get the GCP Project ID from environment variables
PROJECT_ID = os.environ.get('GCP_PROJECT_ID')

def get_secret(secret_id, version_id="latest"):
    """Fetch a secret from Google Cloud Secret Manager."""
    if not PROJECT_ID:
        raise Exception("GCP_PROJECT_ID environment variable is not set!")

    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"
    try:
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode('UTF-8')
    except Exception as e:
        print(f"Error fetching secret '{secret_id}': {e}")
        # In a production environment, you might want to handle this more gracefully
        # For now, we'll raise the exception to make it clear that a secret is missing.
        raise
