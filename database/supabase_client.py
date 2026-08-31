"""
Supabase Client Connection Manager for AIRA Agent.
Handles cloud authentication, client singleton, and health check diagnostics.
"""

from __future__ import annotations
import os
from typing import Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

try:
    from supabase import create_client, Client
    HAS_SUPABASE_LIB = True
except ImportError:
    HAS_SUPABASE_LIB = False
    Client = None

class SupabaseManager:
    """
    Manages connections to the Supabase Cloud PostgreSQL database.
    """

    _instance: Optional["SupabaseManager"] = None
    _client: Optional[Client] = None

    def __new__(cls) -> "SupabaseManager":
        if cls._instance is None:
            cls._instance = super(SupabaseManager, cls).__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self) -> None:
        url = os.getenv("SUPABASE_URL", "").strip()
        key = (os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")).strip()

        if HAS_SUPABASE_LIB and url and key:
            try:
                self._client = create_client(url, key)
            except Exception:
                self._client = None
        else:
            self._client = None

    def configure(self, url: str, key: str) -> Tuple[bool, str]:
        """Dynamically configures Supabase credentials at runtime."""
        if not HAS_SUPABASE_LIB:
            return False, "supabase-py package is not installed."
        if not url or not key:
            return False, "Supabase URL and API Key cannot be empty."

        try:
            self._client = create_client(url.strip(), key.strip())
            # Save to env
            os.environ["SUPABASE_URL"] = url.strip()
            os.environ["SUPABASE_KEY"] = key.strip()
            return True, "Supabase client configured successfully."
        except Exception as ex:
            self._client = None
            return False, f"Failed to initialize Supabase client: {str(ex)}"

    def get_client(self) -> Optional[Client]:
        """Returns the active Supabase client or None if unconfigured."""
        return self._client

    def is_connected(self) -> bool:
        """Checks if a valid Supabase client instance exists."""
        return self._client is not None

    def ping(self) -> Tuple[bool, str]:
        """Tests live database connectivity by querying the aira_tasks table."""
        if not self._client:
            return False, "Supabase is not configured. Provide SUPABASE_URL and SUPABASE_KEY."
        try:
            res = self._client.table("aira_tasks").select("id").limit(1).execute()
            return True, "Supabase Cloud Database connected and healthy."
        except Exception as ex:
            # If table doesn't exist yet, client is connected but needs migration
            err_msg = str(ex)
            if "relation \"public.aira_tasks\" does not exist" in err_msg or "PGRST204" in err_msg:
                return True, "Supabase connected! (Run scripts/init_supabase.sql in SQL Editor to create tables)"
            return False, f"Supabase connection error: {err_msg}"
