"""Google OAuth 2.0 + DUOMO 도메인 검증."""
from __future__ import annotations

import os
from typing import Optional

from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as g_requests


class AuthError(Exception):
    """인증 실패."""


def is_allowed_email(email: str, allowed_domain: str) -> bool:
    """이메일 도메인이 allowed_domain과 일치하는지 검증한다."""
    if "@" not in email:
        raise AuthError(f"Not an email: {email}")
    domain = email.split("@", 1)[1].lower()
    return domain == allowed_domain.lower()


def build_flow(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    hd: Optional[str] = None,
) -> Flow:
    """OAuth 흐름 객체 생성. hd=도메인 힌트로 Workspace 한정 로그인 유도."""
    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    flow.redirect_uri = redirect_uri
    if hd:
        flow._authorization_url_kwargs = {"hd": hd}  # type: ignore[attr-defined]
    return flow


def verify_id_token(token: str, client_id: str) -> dict:
    """ID 토큰을 검증하고 페이로드를 반환한다."""
    try:
        payload = id_token.verify_oauth2_token(
            token, g_requests.Request(), client_id
        )
    except ValueError as e:
        raise AuthError(f"Invalid ID token: {e}") from e
    return payload
