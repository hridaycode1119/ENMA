#!/usr/bin/env python3
"""
Google Gmail OAuth 2.0 Interactive Setup Wizard.
Launches the browser authentication flow and stores token.json.
"""

import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.oauth_handler import GoogleOAuthHandler

def main():
    print("=" * 65)
    print(" 📧 GOOGLE GMAIL API OAUTH 2.0 SETUP WIZARD")
    print("=" * 65)

    oauth = GoogleOAuthHandler()

    if not os.path.exists("credentials.json"):
        print("\n❌ 'credentials.json' NOT FOUND in project root!")
        print("\nPlease follow these steps to download your credentials:")
        print(" 1. Go to Google Cloud Console: https://console.cloud.google.com/")
        print(" 2. Enable 'Gmail API'")
        print(" 3. Go to 'APIs & Services' > 'Credentials'")
        print(" 4. Click '+ CREATE CREDENTIALS' > 'OAuth client ID'")
        print(" 5. Choose Application type: 'Desktop App'")
        print(" 6. Click 'Download JSON' and save it as 'credentials.json' in this folder:")
        print(f"    {os.path.abspath('credentials.json')}")
        print("\n" + "=" * 65)
        sys.exit(1)

    print("\n✅ Found 'credentials.json'.")
    print("🌐 Launching browser for Google Account Authorization...")
    print("👉 Please log in and click 'Continue / Allow' to authorize Gmail permissions.")

    try:
        oauth.run_local_login_flow(port=8080)
        print("\n" + "=" * 65)
        print("🎉 SUCCESS: Authorization complete!")
        print(f"👤 Authenticated User : {oauth.get_authenticated_user_email()}")
        print(f"💾 Token Saved To      : {os.path.abspath('token.json')}")
        print("=" * 65)
        print("\nNow you can launch your Streamlit dashboard with live Gmail sending:")
        print("  streamlit run app.py\n")
    except Exception as ex:
        print(f"\n❌ Authentication Error: {str(ex)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
