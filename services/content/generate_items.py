"""Generate items from templates and output to JSON.

Deterministic given a fixed --seed. Two invocations with the same seed produce
byte-identical output. IDs are stable hashes of (skill_id, difficulty,
parameters, question_text), not uuids, so an item that means the same thing
keeps its id across regenerations.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

from curriculum.nsw_year3_6 import get_skill_tree
from templates import TEMPLATES
from templates.base import deterministic_item_id, item_fingerprint

DEFAULT_SEED = 42
DEFAULT_OUTPUT = "output/content_pack_v0.json"
SKILL_TREE_OUTPUT = "output/skill_tree_v0.json"


def generate_all_items(*, seed: int = DEFAULT_SEED, output_path: str | None = DEFAULT_OUTPUT) -> list[dict]:
    """Generate items across all skills. Deterministic under the given seed.

    Passing output_path=None skips the disk write (used by tests).
    """
    random.seed(seed)

    skill_tree = get_skill_tree()
    print(f"Starting item generation (seed={seed})...")
    print(f"Total skills: {len(skill_tree)}")

    seen: set[str] = set()
    items: list[dict] = []
    duplicates = 0
    errors = 0

    for skill in skill_tree:
        skill_id = skill["skill_id"]
        difficulty_levels = skill["difficulty_levels"]

        # Deterministic template order — same seed + same code = same output.
        skill_templates = sorted(
            [t for t in TEMPLATES if t.skill_id == skill_id],
            key=lambda t: t.__name__,
        )
        if not skill_templates:
            print(f"⚠️  No templates for skill: {skill_id}")
            continue

        print(f"Generating for {skill_id} (Year {skill['year_level']}) — {len(skill_templates)} templates")

        for template in skill_templates:
            for difficulty in difficulty_levels:
                item_count = getattr(template, "items_per_difficulty", 10)
                for _ in range(item_count):
                    try:
                        item = template.generate(difficulty)
                    except Exception as exc:
                        errors += 1
                        print(
                            f"❌ generate error skill={skill_id} diff={difficulty} "
                            f"template={template.__name__}: {exc}"
                        )
                        continue

                    # Rewrite item_id — templates may still produce uuid-based ids
                    # for backward compatibility; the deterministic hash overwrites.
                    item["item_id"] = deterministic_item_id(
                        skill_id=item["skill_id"],
                        difficulty=item["difficulty"],
                        parameters=item.get("parameters", {}),
                        question_text=item.get("question_text", ""),
                    )

                    fp = item_fingerprint(item)
                    if fp in seen:
                        duplicates += 1
                        continue
                    seen.add(fp)
                    items.append(item)

    if output_path is not None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(items, f, indent=2)

    attempted = len(items) + duplicates
    print()
    print(
        f"✅ Generated {len(items)} unique items "
        f"(attempted {attempted}, dropped {duplicates} duplicates, {errors} errors)"
    )
    if output_path is not None:
        print(f"📦 Saved to {output_path}")

    counts = Counter(item["skill_id"] for item in items)
    print("\n📊 Unique items per skill:")
    for skill_id in sorted(counts):
        print(f"  {skill_id}: {counts[skill_id]}")

    return items


def generate_skill_tree_json(output_path: str = SKILL_TREE_OUTPUT) -> None:
    tree = get_skill_tree()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(tree, f, indent=2)
    print(f"✅ Skill tree saved to {output_path} ({len(tree)} skills)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MathCoach content generator")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="RNG seed (default 42)")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT, help="Content pack output path")
    parser.add_argument("--skill-tree-output", type=str, default=SKILL_TREE_OUTPUT)
    args = parser.parse_args(argv)

    print("=" * 60)
    print("MathCoach Content Generator")
    print("=" * 60)
    print()
    generate_skill_tree_json(args.skill_tree_output)
    print()
    generate_all_items(seed=args.seed, output_path=args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
