"""
Google Workspace connector — Gmail, Calendar, Drive.

Auth: credentials are built from secrets stored in Vault at
``secret/data/eva-syndicate/google_workspace``. Two credential modes are supported:
  1. OAuth2 installed-app refresh token:
     keys: oauth_client_id, oauth_client_secret, oauth_refresh_token
  2. Service account:
     key: service_account_json  (full JSON string)

ZERO-TRUST MAIL RULE (per EVA_TOOLKIT_SPEC §7.2): outbound email is NEVER sent
automatically. This connector can only create Gmail DRAFTS. A human (Andrii)
performs the final send.
"""

from __future__ import annotations

import asyncio
import base64
import json
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

import structlog

from src.integrations.base import BaseConnector, ConnectorError

logger = structlog.get_logger(__name__)

try:
    from google.oauth2.credentials import Credentials
    from google.oauth2.service_account import Credentials as SACredentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    _GOOGLE_AVAILABLE = True
except ImportError:  # pragma: no cover
    _GOOGLE_AVAILABLE = False


SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive",
]


class GoogleWorkspaceConnector(BaseConnector):
    """Async wrapper over the (sync) Google API Python client."""

    SERVICE_NAME = "google_workspace"

    def __init__(self, vault_client: Any = None, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(vault_client, config)
        self._creds = None
        self._gmail = None
        self._calendar = None
        self._drive = None

    async def _ensure_clients(self) -> None:
        if not _GOOGLE_AVAILABLE:
            raise ConnectorError(
                "google-api-python-client / google-auth not installed; "
                "install requirements to use GoogleWorkspaceConnector."
            )
        if self._creds is not None:
            return

        # Prefer service account if present, else OAuth refresh token.
        sa_json: Optional[str] = None
        try:
            sa_json = await self._get_secret("service_account_json")
        except ConnectorError:
            sa_json = None

        def _build_creds():
            if sa_json:
                info = json.loads(sa_json)
                return SACredentials.from_service_account_info(info, scopes=SCOPES)
            return None

        creds = await asyncio.to_thread(_build_creds)

        if creds is None:
            client_id = await self._get_secret("oauth_client_id")
            client_secret = await self._get_secret("oauth_client_secret")
            refresh_token = await self._get_secret("oauth_refresh_token")
            creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                client_id=client_id,
                client_secret=client_secret,
                token_uri="https://oauth2.googleapis.com/token",
                scopes=SCOPES,
            )

        self._creds = creds
        self._gmail = await asyncio.to_thread(
            build, "gmail", "v1", credentials=creds, cache_discovery=False
        )
        self._calendar = await asyncio.to_thread(
            build, "calendar", "v3", credentials=creds, cache_discovery=False
        )
        self._drive = await asyncio.to_thread(
            build, "drive", "v3", credentials=creds, cache_discovery=False
        )
        logger.info("google_workspace_clients_ready")

    # ------------------------------------------------------------------- Gmail
    async def list_messages(self, query: str = "", max_results: int = 20) -> List[Dict[str, Any]]:
        await self._ensure_clients()

        def _call():
            res = self._gmail.users().messages().list(
                userId="me", q=query, maxResults=max_results
            ).execute()
            return res.get("messages", [])

        return await asyncio.to_thread(_call)

    async def get_message(self, msg_id: str) -> Dict[str, Any]:
        await self._ensure_clients()

        def _call():
            return self._gmail.users().messages().get(
                userId="me", id=msg_id, format="full"
            ).execute()

        return await asyncio.to_thread(_call)

    async def create_draft(self, to: str, subject: str, body_html: str) -> Dict[str, Any]:
        """Create a Gmail DRAFT. NEVER sends — human confirms the send (Zero-Trust)."""
        await self._ensure_clients()

        def _call():
            msg = MIMEText(body_html, "html")
            msg["to"] = to
            msg["subject"] = subject
            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            return self._gmail.users().drafts().create(
                userId="me", body={"message": {"raw": raw}}
            ).execute()

        result = await asyncio.to_thread(_call)
        logger.info("gmail_draft_created", to=to, subject=subject, draft_id=result.get("id"))
        return result

    # ---------------------------------------------------------------- Calendar
    async def list_events(
        self, time_min: str, time_max: str, calendar_id: str = "primary"
    ) -> List[Dict[str, Any]]:
        await self._ensure_clients()

        def _call():
            res = self._calendar.events().list(
                calendarId=calendar_id, timeMin=time_min, timeMax=time_max,
                singleEvents=True, orderBy="startTime",
            ).execute()
            return res.get("items", [])

        return await asyncio.to_thread(_call)

    async def create_event(
        self, summary: str, start: str, end: str, description: str = "",
        calendar_id: str = "primary",
    ) -> Dict[str, Any]:
        await self._ensure_clients()

        def _call():
            body = {
                "summary": summary,
                "description": description,
                "start": {"dateTime": start},
                "end": {"dateTime": end},
            }
            return self._calendar.events().insert(calendarId=calendar_id, body=body).execute()

        return await asyncio.to_thread(_call)

    # ------------------------------------------------------------------- Drive
    async def list_files(self, query: str = "") -> List[Dict[str, Any]]:
        await self._ensure_clients()

        def _call():
            res = self._drive.files().list(
                q=query, fields="files(id, name, mimeType, modifiedTime, size)"
            ).execute()
            return res.get("files", [])

        return await asyncio.to_thread(_call)

    async def upload_file(
        self, name: str, mime_type: str, local_path: str, folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        await self._ensure_clients()

        def _call():
            metadata: Dict[str, Any] = {"name": name}
            if folder_id:
                metadata["parents"] = [folder_id]
            media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
            return self._drive.files().create(
                body=metadata, media_body=media, fields="id, name"
            ).execute()

        return await asyncio.to_thread(_call)

    async def download_file(self, file_id: str, dest_path: str) -> str:
        await self._ensure_clients()

        def _call():
            request = self._drive.files().get_media(fileId=file_id)
            with open(dest_path, "wb") as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
            return dest_path

        return await asyncio.to_thread(_call)

    # ------------------------------------------------------------------ health
    async def health_check(self) -> Dict[str, Any]:
        try:
            await self._ensure_clients()

            def _call():
                return self._gmail.users().getProfile(userId="me").execute()

            profile = await asyncio.to_thread(_call)
            return {
                "service": self.SERVICE_NAME,
                "healthy": True,
                "detail": {"email": profile.get("emailAddress")},
            }
        except Exception as exc:  # noqa: BLE001
            return {"service": self.SERVICE_NAME, "healthy": False, "detail": str(exc)}
