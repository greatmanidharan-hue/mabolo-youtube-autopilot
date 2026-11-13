from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOKEN_FILE = ROOT / "token.json"
CLIENT_FILE = ROOT / "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def build_video_body(draft: dict[str, Any], privacy: str = "private") -> dict[str, Any]:
    if privacy not in {"private", "unlisted", "public"}:
        raise ValueError("privacy must be private, unlisted or public")
    if privacy == "public":
        if draft.get("editorial_reviewed") is not True:
            raise ValueError("Public upload blocked: set editorial_reviewed=true only after a human review.")
        if not draft.get("source_urls"):
            raise ValueError("Public upload blocked: add verified source_urls before publishing.")
    title = str(draft.get("title") or draft.get("topic") or "Tamil History").strip()
    description = str(draft.get("description") or "").strip()
    hashtags = draft.get("hashtags") or []
    if hashtags:
        description = (description + "\n\n" + " ".join(str(tag) for tag in hashtags)).strip()
    return {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": ["Tamil History", "தமிழ் வரலாறு", "Tamil Shorts"],
            "categoryId": "27"
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False
        }
    }


def upload_video(video_path: Path, draft_path: Path, privacy: str = "private") -> str:
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError as exc:
        raise RuntimeError(
            "YouTube upload packages are missing. Install requirements-youtube.txt."
        ) from exc

    if not CLIENT_FILE.exists():
        raise FileNotFoundError(
            "client_secret.json is missing. Download an OAuth Desktop app client from Google Cloud."
        )
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    body = build_video_body(draft, privacy)

    credentials = None
    if TOKEN_FILE.exists():
        credentials = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_FILE), SCOPES)
        credentials = flow.run_local_server(port=0, access_type="offline", prompt="consent")
        TOKEN_FILE.write_text(credentials.to_json(), encoding="utf-8")

    youtube = build("youtube", "v3", credentials=credentials)
    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        _, response = request.next_chunk()
    video_id = response["id"]
    print(f"Upload complete: https://www.youtube.com/watch?v={video_id}")
    print(f"Privacy status: {privacy}")
    return video_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload a reviewed MABOLO video to YouTube.")
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--draft", type=Path, required=True)
    parser.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private")
    parser.add_argument("--confirm-upload", action="store_true",
                        help="Required to perform an actual YouTube upload.")
    args = parser.parse_args()
    if not args.confirm_upload:
        print("DRY RUN: no upload performed.")
        print(f"Video: {args.video}")
        print(f"Draft: {args.draft}")
        print(f"Requested privacy: {args.privacy}")
        print("Review the files, then repeat with --confirm-upload.")
        return
    upload_video(args.video, args.draft, args.privacy)


if __name__ == "__main__":
    main()
