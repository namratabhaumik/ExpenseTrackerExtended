import os

# Determine environment
CLOUD_RUN = os.environ.get('CLOUD_RUN', 'false').lower() == 'true'

if CLOUD_RUN:
    # Import only in Cloud Run to avoid requiring credentials in CI/local
    from google.cloud import secretmanager
    _client = secretmanager.SecretManagerServiceClient()
    _project_id = os.environ.get('GCP_PROJECT_ID')

def get_secret(secret_id: str, version_id: str = "latest") -> str | None:
    """Fetch a secret from Google Cloud Secret Manager."""
    # Always prefer environment variable value (works for local dev & CI)
    env_val = os.getenv(secret_id)
    if env_val:
        return env_val

    # If not running on Cloud Run, return None (caller should handle missing secret)
    if not CLOUD_RUN:
        return None

    if CLOUD_RUN and not _project_id:
        raise RuntimeError("GCP_PROJECT_ID env var must be set in Cloud Run")
        raise Exception("GCP_PROJECT_ID environment variable is not set!")

    name = f"projects/{_project_id}/secrets/{secret_id}/versions/{version_id}"
    try:
        response = _client.access_secret_version(request={"name": name})
        return response.payload.data.decode()
    except Exception as exc:
        raise RuntimeError(f"Unable to fetch secret '{secret_id}': {exc}") from exc
