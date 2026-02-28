from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from hmac import compare_digest, new as hmac_new
import json

from ..config import settings


def create_access_token(
    *,
    subject: str,
    role: str,
    parent_id: str | None = None,
    expires_minutes: int | None = None,
) -> str:
    ttl = expires_minutes if expires_minutes is not None else settings.token_expire_minutes
    exp = datetime.now(timezone.utc) + timedelta(minutes=ttl)
    payload = {
        "sub": subject,
        "role": role,
        "exp": int(exp.timestamp()),
    }
    if parent_id:
        payload["parent_id"] = parent_id

    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _b64url_json(header)
    payload_b64 = _b64url_json(payload)
    signature = _sign(f"{header_b64}.{payload_b64}")
    return f"{header_b64}.{payload_b64}.{signature}"


def decode_access_token(token: str) -> dict:
    try:
        header_b64, payload_b64, signature = token.split(".")
    except ValueError as exc:
        raise ValueError("Malformed token") from exc

    expected = _sign(f"{header_b64}.{payload_b64}")
    if not compare_digest(signature, expected):
        raise ValueError("Invalid token signature")

    payload = _json_from_b64url(payload_b64)
    if "exp" not in payload:
        raise ValueError("Missing token expiry")
    if int(payload["exp"]) < int(datetime.now(timezone.utc).timestamp()):
        raise ValueError("Token expired")
    return payload


def _sign(value: str) -> str:
    mac = hmac_new(settings.secret_key.encode("utf-8"), value.encode("utf-8"), sha256).digest()
    return _b64url_bytes(mac)


def _b64url_json(value: dict) -> str:
    raw = json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return _b64url_bytes(raw)


def _json_from_b64url(value: str) -> dict:
    raw = _unb64url(value)
    return json.loads(raw.decode("utf-8"))


def _b64url_bytes(value: bytes) -> str:
    return urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _unb64url(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return urlsafe_b64decode((value + padding).encode("ascii"))
