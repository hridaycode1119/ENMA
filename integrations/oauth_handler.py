"""
Google OAuth 2.0 Authorization & Token Lifecycle Manager.
"""

from __future__ import annotations
import json
import os
import time
from typing import Any, Dict, List, Optional

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/userinfo.email",
]

class GoogleOAuthHandler:
    """
    Manages Google OAuth 2.0 user credentials, tokens, and automated refresh cycles.
    """

    def __init__(
        self,
        credentials_file: str = "credentials.json",
        token_file: str = "token.json",
        scopes: Optional[List[str]] = None,
    ):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.scopes = scopes or SCOPES
        self._cached_token_data: Optional[Dict[str, Any]] = None

    def is_authenticated(self) -> bool:
        """Checks if a valid, unexpired token exists or if refresh token is available."""
        if not os.path.exists(self.token_file):
            return False
        try:
            token_data = self._load_token_data()
            if not token_data or not token_data.get("access_token"):
                return False
            # Check expiry with 60s buffer
            expiry = token_data.get("expiry_timestamp", 0)
            if expiry > time.time() + 60:
                return True
            # Expired, check if refresh token exists
            return bool(token_data.get("refresh_token"))
        except Exception:
            return False

    def get_access_token(self) -> Optional[str]:
        """Returns a valid access token, auto-refreshing if expired."""
        if not os.path.exists(self.token_file):
            return None

        token_data = self._load_token_data()
        if not token_data:
            return None

        expiry = token_data.get("expiry_timestamp", 0)
        # If token is still valid, return it
        if expiry > time.time() + 60:
            return token_data.get("access_token")

        # Attempt token refresh
        refresh_token = token_data.get("refresh_token")
        if refresh_token:
            refreshed = self._refresh_access_token(token_data)
            if refreshed:
                return refreshed.get("access_token")

        return token_data.get("access_token")

    def _load_token_data(self) -> Optional[Dict[str, Any]]:
        if not os.path.exists(self.token_file):
            return None
        try:
            with open(self.token_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def save_token_data(self, token_data: Dict[str, Any]) -> None:
        """Persists token dictionary to token.json."""
        with open(self.token_file, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=2)

    def _refresh_access_token(self, token_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Refreshes expired access token using Google token endpoint or client secrets."""
        # Check if credentials.json is present
        if not os.path.exists(self.credentials_file):
            return None
        try:
            with open(self.credentials_file, "r", encoding="utf-8") as f:
                client_config = json.load(f)

            client_info = client_config.get("installed", client_config.get("web", {}))
            client_id = client_info.get("client_id")
            client_secret = client_info.get("client_secret")
            refresh_token = token_data.get("refresh_token")

            if not (client_id and client_secret and refresh_token):
                return None

            import urllib.request
            import urllib.parse

            token_url = "https://oauth2.googleapis.com/token"
            payload = urllib.parse.urlencode({
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }).encode("utf-8")

            req = urllib.request.Request(token_url, data=payload, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                new_token_data = dict(token_data)
                new_token_data["access_token"] = result["access_token"]
                new_token_data["expiry_timestamp"] = time.time() + result.get("expires_in", 3600)
                self.save_token_data(new_token_data)
                return new_token_data
        except Exception:
            return None

    def create_mock_authenticated_session(self, user_email: str = "demo.user@enterprise.com") -> None:
        """Generates a mock authenticated session for tests and offline development."""
        mock_data = {
            "access_token": "mock_oauth_access_token_xyz123",
            "refresh_token": "mock_oauth_refresh_token_abc456",
            "expiry_timestamp": time.time() + 3600,
            "user_email": user_email,
            "scopes": self.scopes,
            "is_mock": True
        }
        self.save_token_data(mock_data)

    def get_authenticated_user_email(self) -> Optional[str]:
        """Returns the cached user email associated with the token session."""
        token_data = self._load_token_data()
        if token_data:
            return token_data.get("user_email") or token_data.get("email")
        return None

    def run_local_login_flow(self, port: int = 8080) -> bool:
        """
        Launches local web browser to authenticate with Google OAuth 2.0.
        Requires valid credentials.json in project root.
        """
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"Missing '{self.credentials_file}'. Please download OAuth Client credentials from Google Cloud Console."
            )

        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            import urllib.request

            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file,
                scopes=self.scopes,
            )
            creds = flow.run_local_server(port=port, prompt="consent", access_type="offline")

            # Query user email from Google UserInfo endpoint
            user_email = None
            try:
                userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
                req = urllib.request.Request(userinfo_url, headers={"Authorization": f"Bearer {creds.token}"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    profile = json.loads(resp.read().decode("utf-8"))
                    user_email = profile.get("email")
            except Exception:
                pass

            token_data = {
                "access_token": creds.token,
                "refresh_token": creds.refresh_token,
                "expiry_timestamp": creds.expiry.timestamp() if creds.expiry else time.time() + 3600,
                "user_email": user_email or "authenticated.user@gmail.com",
                "scopes": self.scopes,
                "is_mock": False,
            }
            self.save_token_data(token_data)
            return True
        except Exception as ex:
            raise RuntimeError(f"Google OAuth authorization failed: {str(ex)}")
