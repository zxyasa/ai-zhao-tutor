#!/usr/bin/env python3
"""
Phase 8 release readiness checks for API configuration hardening.
"""

from app.config import settings


def main() -> int:
    errors = settings.production_validation_errors()
    mode = settings.environment
    print(f"[phase8-check] environment={mode}")

    if not errors:
        print("[phase8-check] OK: runtime configuration checks passed.")
        return 0

    print("[phase8-check] FAILED:")
    for issue in errors:
        print(f"- {issue}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
