import os

# fill all of them
os.environ["GCP_PROJECT_NUMBER"] = os.environ.get("GCP_PROJECT_NUMBER", "FILL_HERE_IF_NOT_SET")
os.environ["PROJECT_ID"] = os.environ.get("PROJECT_ID", "FILL_HERE_IF_NOT_SET")
os.environ["LOCATION"] = os.environ.get("LOCATION", "FILL_HERE_IF_NOT_SET")
os.environ["ENGINE"] = os.environ.get("ENGINE", "FILL_HERE_IF_NOT_SET")
os.environ["WORKFORCE_POOL_ID"] = os.environ.get("WORKFORCE_POOL_ID", "FILL_HERE_IF_NOT_SET")
os.environ["PROVIDER_ID"] = os.environ.get("PROVIDER_ID", "FILL_HERE_IF_NOT_SET")

# Your IDP application details, Entra ID example
os.environ["CLIENT_ID"] = os.environ.get("CLIENT_ID", "FILL_HERE_IF_NOT_SET")
os.environ["CLIENT_SECRET"] = os.environ.get("CLIENT_SECRET", "FILL_HERE_IF_NOT_SET")
os.environ["TENANT_ID"] = os.environ.get("TENANT_ID", "FILL_HERE_IF_NOT_SET")
