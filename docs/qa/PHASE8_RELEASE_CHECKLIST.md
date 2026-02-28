# Phase 8 Release Checklist

## Scope

Phase 8 focuses on authentication, role isolation, and student-context API hardening.

## Pre-Release Config Checks

1. Copy `services/api/.env.example` to `.env`.
2. Set production values:
   - `ENVIRONMENT=production`
   - `DEBUG=false`
   - `SECRET_KEY=<random string, >= 32 chars>`
   - `CORS_ORIGINS_RAW` to real frontend domains only
3. Run config preflight:

```bash
cd services/api
PYTHONPATH=. python scripts/check_phase8_readiness.py
```

Expected: exit code `0` and `OK` output.

## Test Gates

Run backend regression suite:

```bash
cd /Users/michaelzhao/agents/apps/ai-zhao-tutor
.venv/bin/pytest -q services/api/tests
```

Expected: all tests pass (current baseline: `41 passed`).

## iOS Build Gate

```bash
cd /Users/michaelzhao/agents/apps/ai-zhao-tutor
xcodebuild -project apps/ios/MathCoach/MathCoach.xcodeproj \
  -scheme MathCoach \
  -destination 'generic/platform=iOS Simulator' \
  build
```

Expected: `BUILD SUCCEEDED`.

## Functional Smoke

1. Parent login works and can only view own students.
2. Student PIN login works.
3. Student requests use `me` context and cannot query other students.
4. Parent requests without `student_id` on scoped endpoints return `400`.
5. Unauthorized API response triggers iOS token clear and returns to login.

Automated smoke script (requires a running API and seeded accounts):

```bash
cd services/api
export API_BASE_URL=http://127.0.0.1:8000
export PHASE8_PARENT_EMAIL=parent@example.com
export PHASE8_PARENT_PASSWORD=your-parent-password
export PHASE8_STUDENT_ID=jon_zhao
export PHASE8_STUDENT_PIN=1234
PYTHONPATH=. python scripts/smoke_phase8_auth.py
```

Notes:
- Script will auto-attempt parent `register` if `login` fails.
- For parent-only checks, set `PHASE8_SKIP_STUDENT=1`.

## Rollback Notes

If release fails after deploy:
1. Revert to previous API image.
2. Keep DB schema as-is (Phase 8 changes are backward-compatible at app level).
3. Re-run `scripts/check_phase8_readiness.py` on rollback target environment.
