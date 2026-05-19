#!/usr/bin/env python3
"""One-shot uploader: POST 9.2 NEW-skill items to /api/v1/admin/load-items.

Usage:
    ADMIN_LOAD_SECRET=... API_BASE=https://mathcoach-api.micleah.com \
        python upload_new_items_via_admin.py

The admin endpoint runs inside the Railway container and uses the .internal
Postgres URL, so it bulk-inserts at ~1k items/sec instead of the ~50 KB/s
TCP-proxy crawl.

After the upload completes, delete services/api/app/routers/admin.py and the
include in main.py, then redeploy.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests

EXISTING_SKILLS = {
    "jon_carry_add_sub_100",
    "yr2_sem1_add_sub_100",
    "yr2_sem1_compare_100",
    "yr2_sem1_missing_number",
    "yr2_sem1_place_value",
    "yr2_sem1_word_problem",
    "yr3_add_sub_001",
    "yr3_frac_compare_001",
    "yr3_frac_identify_001",
    "yr3_frac_intro_001",
    "yr3_num_place_001",
    "yr4_decimal_001",
    "yr4_frac_compare_002",
    "yr4_frac_equiv_001",
    "yr4_frac_simplify_001",
    "yr4_mult_div_001",
    "yr5_frac_add_001",
    "yr5_frac_add_002",
    "yr5_frac_sub_001",
    "yr5_frac_sub_002",
    "yr5_percent_001",
    "yr6_algebra_001",
    "yr6_frac_div_001",
    "yr6_frac_mixed_001",
    "yr6_frac_mult_001",
    "yr6_ratio_001",
}

CHUNK_SIZE = 500


def main() -> int:
    secret = os.environ.get("ADMIN_LOAD_SECRET")
    if not secret:
        print("ERROR: set ADMIN_LOAD_SECRET env var.", file=sys.stderr)
        return 2

    api_base = os.environ.get("API_BASE", "https://mathcoach-api.micleah.com").rstrip("/")
    url = f"{api_base}/api/v1/admin/load-items"

    content_path = (
        Path(__file__).resolve().parents[2] / "content" / "output" / "content_pack_v0.json"
    )
    if not content_path.exists():
        print(f"ERROR: content pack not found at {content_path}", file=sys.stderr)
        return 2

    with open(content_path) as f:
        all_items = json.load(f)

    new_items = [it for it in all_items if it["skill_id"] not in EXISTING_SKILLS]
    print(
        f"Total items in pack: {len(all_items)}; "
        f"new-skill items to upload: {len(new_items)}"
    )

    new_skill_ids = sorted({it["skill_id"] for it in new_items})
    print(f"New skills ({len(new_skill_ids)}): {new_skill_ids}")

    headers = {"X-Admin-Secret": secret, "Content-Type": "application/json"}

    total_received = 0
    total_inserted = 0
    total_skipped = 0
    failures: list[tuple[int, int, str]] = []

    for offset in range(0, len(new_items), CHUNK_SIZE):
        chunk = new_items[offset : offset + CHUNK_SIZE]
        body = {"items": chunk}
        attempt = 0
        while True:
            attempt += 1
            t0 = time.time()
            try:
                resp = requests.post(url, headers=headers, json=body, timeout=120)
                dt = time.time() - t0
                if resp.status_code != 200:
                    print(
                        f"  chunk @ offset {offset}: HTTP {resp.status_code} "
                        f"in {dt:.1f}s — {resp.text[:200]}"
                    )
                    if attempt < 3:
                        time.sleep(2 * attempt)
                        continue
                    failures.append((offset, len(chunk), resp.text[:200]))
                    break
                data = resp.json()
                total_received += data.get("received", 0)
                total_inserted += data.get("inserted", 0)
                total_skipped += data.get("skipped", 0)
                print(
                    f"  chunk @ offset {offset:>5} ({len(chunk)} items): "
                    f"recv={data.get('received')} ins={data.get('inserted')} "
                    f"skip={data.get('skipped')} in {dt:.1f}s"
                )
                break
            except requests.RequestException as exc:
                print(f"  chunk @ offset {offset}: exception {exc!r}")
                if attempt < 3:
                    time.sleep(2 * attempt)
                    continue
                failures.append((offset, len(chunk), repr(exc)))
                break

    print("")
    print("=" * 60)
    print(f"DONE. received={total_received} inserted={total_inserted} skipped={total_skipped}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for offset, n, msg in failures:
            print(f"  offset {offset} ({n} items): {msg}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
