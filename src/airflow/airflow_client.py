from airflow_client.client import ApiClient, Configuration

from src.envs import (
    AIRFLOW_API_VERSION,
    AIRFLOW_HOST,
    AIRFLOW_JWT_TOKEN,
    AIRFLOW_PASSWORD,
    AIRFLOW_USERNAME,
    AIRFLOW_USE_GCP_AUTH,
)

# Create a configuration and API client
configuration = Configuration(
    host=f"{AIRFLOW_HOST}/api/{AIRFLOW_API_VERSION}",
)

# Set up authentication - priority: GCP > JWT > Basic
if AIRFLOW_USE_GCP_AUTH:
    # Use Google Cloud authentication (for Composer 2)
    import google.auth
    from google.auth.transport.requests import Request

    AUTH_SCOPE = "https://www.googleapis.com/auth/cloud-platform"
    credentials, _ = google.auth.default(scopes=[AUTH_SCOPE])

    # Refresh token if needed
    if not credentials.valid:
        credentials.refresh(Request())

    # Set as Bearer token
    configuration.api_key = {"Authorization": credentials.token}
    configuration.api_key_prefix = {"Authorization": "Bearer"}
elif AIRFLOW_JWT_TOKEN:
    configuration.api_key = {"Authorization": AIRFLOW_JWT_TOKEN}
    configuration.api_key_prefix = {"Authorization": "Bearer"}
elif AIRFLOW_USERNAME and AIRFLOW_PASSWORD:
    configuration.username = AIRFLOW_USERNAME
    configuration.password = AIRFLOW_PASSWORD

api_client = ApiClient(configuration)

# Bearer auth requires manual header setup because auth_settings() in apache-airflow-client 2.x
# only supports Basic authentication.
if AIRFLOW_USE_GCP_AUTH or AIRFLOW_JWT_TOKEN:
    api_client.default_headers["Authorization"] = configuration.get_api_key_with_prefix("Authorization")
