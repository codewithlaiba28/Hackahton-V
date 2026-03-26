"""
Gmail Authentication Script for Customer Success FTE

This script authenticates with Gmail API and saves credentials for automated use.

PREREQUISITES:
1. Google Cloud Project with Gmail API enabled
2. OAuth 2.0 credentials (credentials.json) downloaded
3. credentials.json placed in the backend/ directory

USAGE:
    cd backend
    python gmail_auth.py

WHAT THIS DOES:
1. Opens browser for Google login
2. Requests Gmail permissions (read/send/modify)
3. Saves token.json for automated API access
4. Lists Gmail labels to verify connection

REQUIRED SCOPES:
- https://www.googleapis.com/auth/gmail.modify
  (Read, send, delete, and manage your Gmail messages)

TROUBLESHOOTING:
- If authentication fails, delete token.json and try again
- Ensure credentials.json is in the backend/ directory
- Check that Gmail API is enabled in Google Cloud Console
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError as e:
    print(f"❌ Google API libraries not installed: {e}")
    print("\nInstall with:")
    print("    pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    GOOGLE_AVAILABLE = False
    sys.exit(1)

# Gmail API scope - modify allows read, send, delete, and manage
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Paths
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'


def main():
    """Main authentication flow"""
    print("=" * 70)
    print("📧 GMAIL API AUTHENTICATION")
    print("=" * 70)
    print()
    
    # Check credentials file
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ Credentials file not found: {CREDENTIALS_FILE}")
        print()
        print("SETUP INSTRUCTIONS:")
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Create/select a project")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials (Desktop app)")
        print("5. Download credentials.json")
        print("6. Place it in: backend/credentials.json")
        print()
        sys.exit(1)
    
    print(f"✅ Found credentials: {CREDENTIALS_FILE}")
    print()
    
    creds = None
    
    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        print(f"📄 Found existing token: {TOKEN_FILE}")
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            print("✅ Token loaded successfully")
        except Exception as e:
            print(f"⚠️  Token invalid, will re-authenticate: {e}")
            creds = None
        print()
    
    # Refresh or authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            try:
                creds.refresh(Request())
                print("✅ Token refreshed successfully")
            except Exception as e:
                print(f"⚠️  Refresh failed, will re-authenticate: {e}")
                creds = None
            print()
        
        if not creds or not creds.valid:
            print("🔐 Starting OAuth 2.0 authorization flow...")
            print()
            print("📋 PERMISSIONS REQUESTED:")
            print("   - Read your Gmail messages")
            print("   - Send emails on your behalf")
            print("   - Manage labels and message state")
            print()
            print("👉 A browser window will open. Please:")
            print("   1. Sign in with your Google account")
            print("   2. Review and ACCEPT the permissions")
            print("   3. Return here when complete")
            print()
            input("   Press ENTER to continue to browser...")
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES
                )
                # run_local_server opens browser on port 0 (random available port)
                creds = flow.run_local_server(port=0, open_browser=True)
                print()
                print("✅ Authentication successful!")
            except Exception as e:
                print(f"\n❌ Authentication failed: {e}")
                print("\nTROUBLESHOOTING:")
                print("1. Check that credentials.json is valid")
                print("2. Ensure Gmail API is enabled in Google Cloud Console")
                print("3. Try deleting token.json and running again")
                sys.exit(1)
    
    # Save credentials for future use
    print(f"💾 Saving token to: {TOKEN_FILE}")
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    print("✅ Token saved successfully")
    print()
    
    # Test the connection
    print("🔍 Testing Gmail API connection...")
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Get profile
        profile = service.users().getProfile(userId='me').execute()
        email_address = profile['emailAddress']
        print(f"✅ Connected to: {email_address}")
        
        # Get labels
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        print(f"✅ Gmail API accessible")
        print(f"📑 Found {len(labels)} labels:")
        
        # Show important labels
        important_labels = ['INBOX', 'SENT', 'DRAFTS', 'SPAM', 'TRASH']
        for label in labels:
            if label['name'] in important_labels:
                print(f"   - {label['name']} ({label['messagesTotal']} messages)")
        
        print()
        print("=" * 70)
        print("🎉 GMAIL AUTHENTICATION COMPLETE!")
        print("=" * 70)
        print()
        print("NEXT STEPS:")
        print("1. ✅ Token saved as 'token.json' - API can now access Gmail")
        print("2. ✅ Start the backend: python -m uvicorn api.main:app --reload")
        print("3. ✅ Gmail polling will start automatically")
        print("4. 📧 Send a test email to: " + email_address)
        print()
        print("USAGE:")
        print("- The AI agent will automatically read unread emails")
        print("- Responses will be sent via Gmail API")
        print("- Email threading is preserved (Re: subject)")
        print()
        
    except Exception as error:
        print(f"❌ API test failed: {error}")
        print("\nTROUBLESHOOTING:")
        print("1. Delete token.json and run this script again")
        print("2. Check that Gmail API is enabled in Google Cloud Console")
        print("3. Ensure your Google account has Gmail enabled")
        sys.exit(1)


if __name__ == '__main__':
    main()
