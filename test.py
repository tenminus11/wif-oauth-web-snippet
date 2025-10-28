import os
from google.auth import exceptions
from google.auth import identity_pool
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1
from google.cloud.discoveryengine_v1.types import Query
from config import Config

GCP_PROJECT_NUMBER = os.environ["GCP_PROJECT_NUMBER"]
PROJECT_ID = os.environ["PROJECT_ID"]
WORKFORCE_POOL_ID = os.environ["WORKFORCE_POOL_ID"]
PROVIDER_ID = os.environ["PROVIDER_ID"]
ENTRA_TENANT_ID = os.environ["ENTRA_TENANT_ID"]
LOCATION = os.environ["LOCATION"]
ENGINE = os.environ["ENGINE"]
WIF_AUDIENCE = f"//iam.googleapis.com/locations/global/workforcePools/{WORKFORCE_POOL_ID}/providers/{PROVIDER_ID}"
ID_TOKEN = os.environ["ID_TOKEN"]

client_options = (
    ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
    if LOCATION != "global"
    else None
)

class CustomSubjectTokenSupplier(identity_pool.SubjectTokenSupplier):
    def __init__(self, id_token):
        self._id_token = id_token

    def get_subject_token(self, context, request):
        audience = context.audience
        subject_token_type = context.subject_token_type
        try:
            return self._id_token
            # Attempt to return the valid subject token of the requested type for the requested audience.
        except Exception as e:
            # If token retrieval fails, raise a refresh error, setting retryable to true if the client should
            # attempt to retrieve the subject token again.
            raise exceptions.RefreshError(e, retryable=True)


def get_credentials(id_token):
    supplier = CustomSubjectTokenSupplier(id_token)

    credentials = identity_pool.Credentials(
        WIF_AUDIENCE,
        "urn:ietf:params:oauth:token-type:jwt",
        subject_token_supplier=supplier,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
        workforce_pool_user_project=GCP_PROJECT_NUMBER,
    )
    return credentials


def sample_stream_assist(credentials):
    # Create a client
    client = discoveryengine_v1.AssistantServiceClient(
        credentials=credentials,
        client_options=client_options
    )

    # Initialize request argument(s)
    request = discoveryengine_v1.StreamAssistRequest(
        name=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE}/assistants/default_assistant",
        query=Query(text="list sharepoint files")
    )

    # Make the request
    stream = client.stream_assist(request=request)

    res = ""
    # Handle the response
    for response in stream:
        text = " ".join([r.grounded_content.content.text for r in response.answer.replies])
        print("text", text)
        res = res + " " + text

    return res

cred = get_credentials(ID_TOKEN)
sample_stream_assist(cred)