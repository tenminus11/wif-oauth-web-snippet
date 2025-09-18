class Config:
    """
    Application Configurations
    """

    ENTRA_TENANT_ID = "" # fill this
    CLIENT_ID = ""  # Your Azure application's client ID
    CLIENT_SECRET = ""  # Your Azure application's client secret
    
    SCOPE = f"{CLIENT_ID}/openid offline_access"
    AUTHORIZATION_BASE_URL = f"https://login.microsoftonline.com/{ENTRA_TENANT_ID}/oauth2/v2.0/authorize"
    TOKEN_URL = f"https://login.microsoftonline.com/{ENTRA_TENANT_ID}/oauth2/v2.0/token"
    REDIRECT_URI = "http://localhost:5000/callback"
    
    PROJECT_ID = "" # fill this
    GCP_PROJECT_NUMBER = "" # fill this
    WORKFORCE_POOL_ID = "" # fill this gcp wif pool
    PROVIDER_ID = "" # fill this gcp wif provider

    WIF_AUDIENCE = f"//iam.googleapis.com/locations/global/workforcePools/{WORKFORCE_POOL_ID}/providers/{PROVIDER_ID}"
