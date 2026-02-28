#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="${ROOT_DIR}/services/api"
PY_BIN="python3"

if [[ ! -d "${API_DIR}" ]]; then
  echo "[deploy-check] missing api dir: ${API_DIR}" >&2
  exit 1
fi

if [[ -x "${API_DIR}/.venv/bin/python" ]]; then
  PY_BIN="${API_DIR}/.venv/bin/python"
fi

echo "[deploy-check] api dir: ${API_DIR}"
echo "[deploy-check] running production readiness check with local env if present..."
(
  cd "${API_DIR}"
  PYTHONPATH=. "${PY_BIN}" scripts/check_phase8_readiness.py || true
)

cat <<'EOF'

[railway-required-vars]
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<at least 32 chars>
DATABASE_URL=<Railway Postgres URL>
CORS_ORIGINS_RAW=https://<your-api-domain>

[optional-vars]
OPENAI_API_KEY=<if needed>
SMTP_HOST=<if email enabled>
SMTP_PORT=587
SMTP_USERNAME=<if email enabled>
SMTP_PASSWORD=<if email enabled>
SMTP_SENDER=<if email enabled>

[ios-setting]
Set "MATHCOACH_API_BASE_URL" in Xcode Scheme environment to:
https://<your-api-domain>/api/v1
EOF
