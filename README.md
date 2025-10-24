# WIF-OAuth-Web-Snippet

This repository contains a web snippet that demonstrates how to use Workforce Identity Federation (WIF) with OAuth 2.0 to authenticate users in a web application.

## Overview

The snippet provides a basic web application that allows users to log in using their federated identity. It leverages Workforce Identity Federation to exchange a Entra ID token for a Google Cloud access token, which can then be used to access Google Cloud resources.

## Features

- **Google OAuth 2.0 Integration**: Authenticates users using their Google accounts.
- **Workforce Identity Federation**: Demonstrates how to exchange an ID token for a Google Cloud access token.
- **Client-side and Server-side Flows**: Includes examples for both client-side (implicit flow) and server-side (authorization code flow) authentication.
- **Resource Access Example**: Shows how to use the obtained access token to make a simple API call to a Google Cloud service (e.g., fetching cloud storage info).

## Getting Started

### Prerequisites

Before you begin, ensure you have the following:

- A Google Cloud Project.
- A basic understanding of OAuth 2.0 and Workforce Identity Federation.

### Setup

1. **Create Azure AD App Registration**:
   - Go to the [Azure portal](https://portal.azure.com/).
   - Search for and select "App registrations".
   - Click "New registration".
   - Enter a name for your application (e.g., "WIF OAuth Web Snippet").
   - For "Supported account types", select "Accounts in this organizational directory only (Default Directory only - Single tenant)".
   - For "Redirect URI (optional)", select "Web" and enter your application's redirect URI (e.g., `http://localhost:5000/callback`).
   - Click "Register".
   - After the app is created, note down the **Application (client) ID** and **Directory (tenant) ID**.
   - Go to "Certificates & secrets" and create a new client secret. Note down the **Value** of the client secret (this will only be shown once).
   - Go to "API permissions" and ensure "Microsoft Graph" -> "User.Read", "openid", "profile", "offline_access", "email" Delegated is granted. If not, add it.
   - Go to "Expose an API" and click "Add a scope".
   - Set "Application ID URI" to `api://YOUR_CLIENT_ID` (replace `YOUR_CLIENT_ID` with your Application (client) ID).
   - Define a scope name `openid`.
   - Configure consent and state values as needed.
   - Click "Add scope".
   - Go to "Token configuration" and click "Add optional claim".
   - Add "email" claim for both "ID", "Access" for the token type.
   - Add "group" claim for "ID", "Access" & "SAML" for the token type. Make sure Group ID is selected.



2. **Configure Workforce Identity Federation & IAM access**:
   - Follow the instructions in the [Google Cloud documentation](https://cloud.google.com/iam/docs/workforce-sign-in-microsoft-entra-id) to set up a Workforce Identity Pool and Provider.
   - Grant the necessary IAM roles to user principal to test access \
     Example : Grant the `Storage Bucket Viewer` role to the workforce pool user on the bucket you want to access. \
     `gcloud projects add-iam-policy-binding YOUR_PROJECT_ID --member="principalSet://iam.googleapis.com/locations/global/workforcePools/YOUR_WORKFORCE_POOL_ID/subject/YOUR_USER_ID" --role="roles/storage.bucketViewer"`

  

3. **Update `config.py`**:
   - Open the `config.py` file.
   - Fill in the `ENTRA_TENANT_ID`, `CLIENT_ID`, and `CLIENT_SECRET` with the values obtained from your Azure AD App Registration.
   - Fill in `PROJECT_ID`, `GCP_PROJECT_NUMBER`, `WORKFORCE_POOL_ID`, and `PROVIDER_ID` with your Google Cloud project and Workforce Identity Federation details.

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Application**:
   ```bash
   python main.py
   ```
   The application will start on `http://localhost:5000`.

## Usage

1. Open your web browser and navigate to `http://localhost:5000`.
2. Click the "Log in with OAuth Provider" button.
3. You will be redirected to the Azure AD login page. Enter your credentials.
4. After successful authentication, you will be redirected back to the application's callback URL.
5. The application will display your access token and other token information, and list the Google Cloud Storage buckets accessible with the federated credentials.
