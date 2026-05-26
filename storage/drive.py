"""Google Drive API 클라이언트 (다운로드·업로드·캐시)."""
from __future__ import annotations

import io
import logging
import time
from pathlib import Path
from typing import Optional

from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

log = logging.getLogger(__name__)


class DriveError(Exception):
    """Drive API 호출 실패."""


class DriveClient:
    """Drive API 래퍼. 다운로드 결과는 cache_dir에 저장된다."""

    def __init__(self, service, cache_dir: Path):
        self.service = service
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def download(self, drive_id: str, mime_suffix: str = ".jpg") -> Path:
        """drive_id를 다운로드해서 cache_dir에 저장하고 경로를 반환한다.

        이미 캐시에 있으면 API 호출하지 않는다.
        실패 시 3회까지 지수 백오프 재시도.
        """
        cached = self.cache_dir / f"{drive_id}{mime_suffix}"
        if cached.exists():
            log.debug("cache hit: %s", drive_id)
            return cached

        last_err: Optional[Exception] = None
        for attempt in range(3):
            try:
                request = self.service.files().get_media(fileId=drive_id)
                buffer = io.BytesIO()
                downloader = MediaIoBaseDownload(buffer, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
                cached.write_bytes(buffer.getvalue())
                return cached
            except Exception as e:
                last_err = e
                wait = 2 ** attempt
                log.warning("drive download failed (attempt %d): %s — retry in %ds",
                            attempt + 1, e, wait)
                time.sleep(wait)

        raise DriveError(f"Failed to download {drive_id} after 3 attempts: {last_err}")

    def upload(self, local_path: Path, parent_folder_id: str, name: Optional[str] = None) -> str:
        """로컬 파일을 Drive에 업로드하고 생성된 파일의 ID를 반환한다."""
        metadata = {
            "name": name or local_path.name,
            "parents": [parent_folder_id],
        }
        media = MediaFileUpload(str(local_path), resumable=True)
        try:
            created = self.service.files().create(
                body=metadata, media_body=media, fields="id"
            ).execute()
            return created["id"]
        except Exception as e:
            raise DriveError(f"Failed to upload {local_path}: {e}") from e
