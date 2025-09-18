import os
import requests
from google.auth import exceptions
from google.auth import identity_pool
import json
from google.cloud import storage


from flask import Flask, session, request, render_template
import config
from pprint import pprint

# initializing configurations
conf = config.Config()

app = Flask(__name__)
# A secret key is required for session management in Flask
# In a production environment, generate a strong, random key: os.urandom(24)
app.secret_key = "12345"

# --- OAuth 2.0 Configuration ---
# IMPORTANT: Replace these with your actual OAuth provider details
AUTHORIZATION_BASE_URL = conf.AUTHORIZATION_BASE_URL
TOKEN_URL = conf.TOKEN_URL
REDIRECT_URI = conf.REDIRECT_URI

CLIENT_ID = conf.CLIENT_ID  # Your application's client ID
CLIENT_SECRET = conf.CLIENT_SECRET
WIF_AUDIENCE = conf.WIF_AUDIENCE
GCP_PROJECT_NUMBER = conf.GCP_PROJECT_NUMBER
PROJECT_ID  = conf.PROJECT_ID
SCOPE = conf.SCOPE


# DOC https://github.com/googleapis/google-auth-library-python/blob/main/docs/user-guide.rst#accessing-resources-using-a-custom-supplier-with-oidc-or-saml

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
        workforce_pool_user_project=GCP_PROJECT_NUMBER
    )
    return credentials


def list_gcp_storage_buckets(credentials):
    """
    Lists GCP storage buckets using the generated credentials.
    """
    try:
        client = storage.Client(credentials=credentials, project=PROJECT_ID)
        buckets = client.list_buckets()
        print("Buckets in project:")
        buckets_names = [bucket.name for bucket in buckets]
        print("\n".join(buckets_names))
        return buckets_names
    except Exception as e:
        print(f"Failed to list GCP storage buckets: {e}")
        raise



@app.route("/")
def index():
    """
    Home page that initiates the OAuth 2.0 authorization flow.
    It constructs the authorization URL and redirects the user's browser.
    """
    # Generate a random state for CSRF protection
    state = os.urandom(16).hex()
    session["oauth_state"] = state

    # Construct the authorization URL
    auth_url = (
        f"{AUTHORIZATION_BASE_URL}?"
        f"response_type=code&"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"scope={SCOPE}&"
        f"state={state}"
    )

    return render_template("index.html", auth_url=auth_url)


@app.route("/callback")
def callback():
    """
    OAuth 2.0 callback endpoint.
    This route receives the authorization code from the OAuth provider
    and exchanges it for an access token.
    """
    # Verify the state parameter to prevent CSRF
    expected_state = session.pop("oauth_state", None)
    received_state = request.args.get("state")

    if not received_state or received_state != expected_state:
        return "State mismatch or missing. Possible CSRF attack.", 400

    # Get the authorization code from the URL parameters
    authorization_code = request.args.get("code")

    if not authorization_code:
        error = request.args.get("error", "No authorization code received.")
        error_description = request.args.get(
            "error_description", "Please check the console for more details."
        )
        return f"OAuth error: {error}. Description: {error_description}", 400

    # Exchange the authorization code for an access token
    token_data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    try:
        response = requests.post(
            TOKEN_URL, data=token_data, headers={"Accept": "application/json"}
        )
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        token_info = response.json()
        pprint(token_info)
        access_token = token_info.get("access_token")
        refresh_token = token_info.get(
            "refresh_token"
        )  # Optional, if provider supports it
        expires_in = token_info.get("expires_in")
        token_type = token_info.get("token_type")
        id_token = token_info.get("id_token")


        session["access_token"] = access_token

        # In a real application, you would store tokens securely (e.g., in a database)
        # and use them to make API calls on behalf of the user.
        gcp_cred = get_credentials(id_token)

        return render_template(
            "token_display.html",
            access_token=access_token,
            id_token=id_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            token_type=token_type,
            buckets=", ".join(
                list_gcp_storage_buckets(gcp_cred))
        )

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error exchanging code for token: {e}")
        return f"Failed to exchange authorization code for token: {e}", 500
    except ValueError as e:
        app.logger.error(f"Error parsing token response: {e}")
        return (
            f"Failed to parse token response: {e}. Raw response: {response.text if 'response' in locals() else 'N/A'}",
            500,
        )


if __name__ == "__main__":
    # Run the Flask app
    # In a production environment, use a production-ready WSGI server like Gunicorn
    app.run(debug=True, port=5000)

