# Phase 8 Release Approval

## Change Window

- **Date:** 2026-07-04
- **Time Window:** 2026-07-04 20:00 – 22:00 AEST
- **Owner:** Michael Zhao (Micleah Pty Ltd)

## Scope Confirmation

- [x] Auth routes (`/auth/register`, `/auth/login`, `/auth/student-login`)
- [x] Role isolation (`parent` vs `student`)
- [x] `me` endpoints for student context
- [x] iOS token lifecycle (Keychain + 401 auto logout)

## Evidence

- Backend tests: `41 passed` (verified 2026-02-21 baseline)
- iOS build: `BUILD SUCCEEDED` (target `Sweetsworld.MathCoach`, team `7W37S94W3G`)
- Config preflight: `scripts/check_phase8_readiness.py` passed
- E2E smoke: `scripts/smoke_phase8_auth.py` passed
- Production deployment: `https://mathcoach-api.micleah.com/` LIVE on Railway
  - `/health` → 200
  - `/docs` (Swagger UI) → 200
  - `/api/v1/students` → 401 (auth gate correct)

## Risk Assessment

- **Known risks:**
  - Single-parent scope in production (only Michael's family) — limited blast radius
  - Existing token in transit (issued > 30d ago) may need first-parent re-register post-deploy — mitigation: Phase 8 register endpoint is idempotent
  - No CI/CD pipeline yet — deploys are manual via Railway
- Rollback plan reviewed: [x] yes
  - Revert to previous Railway image via dashboard (last known good)
  - DB schema is backward-compatible; no downgrade required
- Data migration impact reviewed: [x] yes
  - Phase 8 introduces `parents` table + `students.parent_id` + `students.pin_hash` — all additive, no destructive migrations

## Sign-off

- **Engineering:** Michael Zhao — 2026-07-04
- **Product:** Michael Zhao — 2026-07-04
- **Ops:** Michael Zhao — 2026-07-04
- **Final Go/No-Go:** ✅ **GO** — 2026-07-04

## Post-Release Checklist

- [ ] Seed `jon_zhao` + `astrid_zhao` via `services/api/scripts/seed_students.py` on Railway
- [ ] Register parent account (Michael's email)
- [ ] Set PIN for Jon + Astrid
- [ ] Xcode archive → TestFlight upload
- [ ] Invite `jon.m.zhao@icloud.com` + `astrid.zhao@icloud.com` as TestFlight testers
- [ ] iPad install + first-session validation
