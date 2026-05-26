"""storage.drive tests with mocked Google Drive API."""
import io
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from storage.drive import DriveClient, DriveError


def test_download_caches_file(tmp_path):
    """이미 캐시된 파일은 API 호출 없이 반환."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    cached_file = cache_dir / "DRIVE_ID_001.jpg"
    cached_file.write_bytes(b"cached-content")

    mock_service = MagicMock()
    client = DriveClient(service=mock_service, cache_dir=cache_dir)

    result = client.download("DRIVE_ID_001")

    assert result == cached_file
    assert result.read_bytes() == b"cached-content"
    mock_service.files().get_media.assert_not_called()


def test_download_fetches_when_not_cached(tmp_path):
    """캐시에 없으면 Drive API 호출 후 캐시에 저장."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()

    mock_service = MagicMock()
    mock_request = MagicMock()
    mock_service.files().get_media.return_value = mock_request

    class FakeDownloader:
        def __init__(self, buf, req):
            self.buf = buf
            self._done = False
        def next_chunk(self):
            self.buf.write(b"fresh-content")
            self._done = True
            return (MagicMock(progress=lambda: 1.0), True)

    with patch("storage.drive.MediaIoBaseDownload", FakeDownloader):
        client = DriveClient(service=mock_service, cache_dir=cache_dir)
        result = client.download("DRIVE_ID_002")

    assert result.exists()
    assert result.read_bytes() == b"fresh-content"
    mock_service.files().get_media.assert_called_with(fileId="DRIVE_ID_002")
