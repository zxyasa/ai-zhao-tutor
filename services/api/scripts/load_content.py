#!/usr/bin/env python3
"""
Load generated content into the database
Run this after generating content with generate_items.py
"""
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal, init_db
from app.models import Item

def load_content():
    """Load content pack into database"""
    # Initialize database
    init_db()

    # Path to content pack
    content_path = Path(__file__).parent.parent.parent / "content" / "output" / "content_pack_v0.json"

    if not content_path.exists():
        print(f"❌ Content pack not found at: {content_path}")
        print("\n💡 Please run generate_items.py first:")
        print("   cd services/content")
        print("   python generate_items.py")
        return False

    # Load content
    with open(content_path) as f:
        items_data = json.load(f)

    print(f"📦 Loading {len(items_data)} items into database...")

    # Create session
    db = SessionLocal()

    try:
        # Clear existing items (optional - comment out to preserve data)
        # db.query(Item).delete()
        # print("🗑️  Cleared existing items")

        # Add items
        items_added = 0
        items_skipped = 0

        for item_data in items_data:
            # Check if item already exists
            existing = db.query(Item).filter(Item.id == item_data['item_id']).first()

            if existing:
                items_skipped += 1
                continue

            item = Item(
                id=item_data['item_id'],
                skill_id=item_data['skill_id'],
                question_text=item_data['question_text'],
                question_type=item_data['question_type'],
                difficulty=item_data['difficulty'],
                parameters=item_data['parameters'],
                correct_answer=item_data['correct_answer'],
                hint=item_data['hint'],
                explanation=item_data['explanation'],
                validation_rule=item_data.get('validation_rule', 'exact_match')
            )
            db.add(item)
            items_added += 1

        db.commit()

        print(f"\n✅ Successfully loaded content:")
        print(f"   Added: {items_added} items")
        if items_skipped > 0:
            print(f"   Skipped: {items_skipped} items (already exist)")

        # Print summary by skill
        print("\n📊 Items by skill:")
        from sqlalchemy import func
        results = db.query(
            Item.skill_id,
            func.count(Item.id).label('count')
        ).group_by(Item.skill_id).all()

        for skill_id, count in results:
            print(f"   {skill_id}: {count} items")

        return True

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error loading content: {e}")
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = load_content()
    sys.exit(0 if success else 1)
