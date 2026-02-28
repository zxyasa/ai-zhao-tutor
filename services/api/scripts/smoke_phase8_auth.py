#!/usr/bin/env python3
"""
Phase 8 auth smoke test against a running API server.

Required environment variables:
  PHASE8_PARENT_EMAIL
  PHASE8_PARENT_PASSWORD
  PHASE8_STUDENT_ID
  PHASE8_STUDENT_PIN

Optional:
  API_BASE_URL (default: http://127.0.0.1:8000)
  PHASE8_SKIP_STUDENT=1  (skip student login + me endpoint checks)
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def _request_json(
    method: str,
    url: str,
    *,
    payload: dict | None = None,
    token: str | None = None,
) -> tuple[int, dict]:
    data = None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        parsed = {}
        if body:
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = {"raw": body}
        return exc.code, parsed


def _must_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def main() -> int:
    base = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    skip_student = os.getenv("PHASE8_SKIP_STUDENT", "0") == "1"
    email = _must_env("PHASE8_PARENT_EMAIL")
    password = _must_env("PHASE8_PARENT_PASSWORD")
    student_id = os.getenv("PHASE8_STUDENT_ID", "").strip()
    student_pin = os.getenv("PHASE8_STUDENT_PIN", "").strip()

    # Parent login
    status, parent_login = _request_json(
        "POST",
        f"{base}/api/v1/auth/login",
        payload={"email": email, "password": password},
    )
    if status != 200:
        # New/ephemeral environments may not have this parent yet.
        reg_status, reg_body = _request_json(
            "POST",
            f"{base}/api/v1/auth/register",
            payload={"email": email, "password": password, "display_name": "Phase8 Smoke Parent"},
        )
        if reg_status not in {200, 409}:
            print(f"[FAIL] parent login/register: login={status} body={parent_login}, register={reg_status} body={reg_body}")
            return 1
        status, parent_login = _request_json(
            "POST",
            f"{base}/api/v1/auth/login",
            payload={"email": email, "password": password},
        )
        if status != 200:
            print(f"[FAIL] parent login after register: status={status}, body={parent_login}")
            return 1
    parent_token = parent_login["access_token"]
    print("[OK] parent login")

    # Parent scoped endpoint should reject /streak/me
    status, body = _request_json(
        "GET",
        f"{base}/api/v1/streak/me",
        token=parent_token,
    )
    if status != 400:
        print(f"[FAIL] parent /streak/me expected 400, got {status}, body={body}")
        return 1
    print("[OK] parent /streak/me requires explicit student_id")

    # Parent explicit student scope
    status, body = _request_json(
        "GET",
        f"{base}/api/v1/streak/{urllib.parse.quote(student_id)}",
        token=parent_token,
    )
    if status != 200:
        print(f"[FAIL] parent /streak/{{student_id}}: status={status}, body={body}")
        return 1
    print("[OK] parent explicit student scope")

    if skip_student:
        print("[SKIP] student checks skipped (PHASE8_SKIP_STUDENT=1)")
        print("[PASS] phase8 auth smoke checks completed (parent scope)")
        return 0

    if not student_id or not student_pin:
        print("[FAIL] PHASE8_STUDENT_ID and PHASE8_STUDENT_PIN are required unless PHASE8_SKIP_STUDENT=1")
        return 1

    # Student login
    status, student_login = _request_json(
        "POST",
        f"{base}/api/v1/auth/student-login",
        payload={"student_id": student_id, "pin": student_pin},
    )
    if status != 200:
        print(f"[FAIL] student login: status={status}, body={student_login}")
        return 1
    student_token = student_login["access_token"]
    print("[OK] student login")

    # Student me endpoints
    status, body = _request_json("GET", f"{base}/api/v1/streak/me", token=student_token)
    if status != 200:
        print(f"[FAIL] student /streak/me: status={status}, body={body}")
        return 1
    status, body = _request_json("GET", f"{base}/api/v1/daily-session/status", token=student_token)
    if status != 200:
        print(f"[FAIL] student /daily-session/status: status={status}, body={body}")
        return 1
    print("[OK] student me endpoints")

    print("[PASS] phase8 auth smoke checks completed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        raise SystemExit(1)
