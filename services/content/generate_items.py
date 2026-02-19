"""
Generate items from templates and output to JSON
Generates deterministic math content for MathCoach platform
"""
import json
from curriculum.nsw_year3_6 import get_skill_tree
from templates import TEMPLATES


def generate_all_items():
    """Generate items for all skills using available templates"""
    all_items = []
    skill_tree = get_skill_tree()

    print("Starting item generation...")
    print(f"Total skills: {len(skill_tree)}")

    for skill in skill_tree:
        skill_id = skill["skill_id"]
        difficulty_levels = skill["difficulty_levels"]

        # Find templates for this skill
        templates = [t for t in TEMPLATES if t.skill_id == skill_id]

        if not templates:
            print(f"⚠️  No templates found for skill: {skill_id}")
            continue

        print(f"Generating for {skill_id} (Year {skill['year_level']}) - {len(templates)} templates")

        for template in templates:
            for difficulty in difficulty_levels:
                item_count = getattr(template, "items_per_difficulty", 10)
                for i in range(item_count):
                    try:
                        item = template.generate(difficulty)
                        all_items.append(item)
                    except Exception as e:
                        print(f"❌ Error generating item: {skill_id}, difficulty {difficulty}, template {template.__name__}")
                        print(f"   Error: {e}")

    # Save to JSON
    output_path = "output/content_pack_v0.json"
    with open(output_path, 'w') as f:
        json.dump(all_items, f, indent=2)

    print(f"\n✅ Generated {len(all_items)} items")
    print(f"📦 Saved to {output_path}")

    # Print summary
    skill_counts = {}
    for item in all_items:
        skill_id = item["skill_id"]
        skill_counts[skill_id] = skill_counts.get(skill_id, 0) + 1

    print("\n📊 Items per skill:")
    for skill_id, count in sorted(skill_counts.items()):
        print(f"  {skill_id}: {count} items")

    return all_items


def generate_skill_tree_json():
    """Generate skill tree JSON file"""
    skill_tree = get_skill_tree()
    output_path = "output/skill_tree_v0.json"

    with open(output_path, 'w') as f:
        json.dump(skill_tree, f, indent=2)

    print(f"✅ Skill tree saved to {output_path}")
    print(f"   Total skills: {len(skill_tree)}")


if __name__ == "__main__":
    print("=" * 60)
    print("MathCoach Content Generator v0.1")
    print("=" * 60)
    print()

    # Generate skill tree
    generate_skill_tree_json()
    print()

    # Generate items
    generate_all_items()
