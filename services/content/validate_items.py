"""
Validate generated items by recomputing answers
Ensures all items have correct, deterministic answers
"""
import json
from fractions import Fraction
import math


def validate_fraction_comparison(item):
    """Validate fraction comparison item"""
    params = item["parameters"]
    num1 = params["num1"]
    num2 = params["num2"]
    denom1 = params["denom1"]
    denom2 = params["denom2"]

    frac1 = Fraction(num1, denom1)
    frac2 = Fraction(num2, denom2)

    if frac1 > frac2:
        expected = f"{num1}/{denom1}"
    else:
        expected = f"{num2}/{denom2}"

    return expected


def validate_fraction_addition(item):
    """Validate fraction addition item"""
    params = item["parameters"]

    # Recompute the answer
    num1 = params["num1"]
    num2 = params["num2"]
    denom1 = params["denom1"]
    denom2 = params["denom2"]

    result = Fraction(num1, denom1) + Fraction(num2, denom2)

    # Check if stored result matches
    stored_result = Fraction(params["result_num"], params["result_denom"])

    if result != stored_result:
        return None  # Invalid

    return f"{params['result_num']}/{params['result_denom']}"


def validate_equivalent_fraction(item):
    """Validate equivalent fraction item"""
    params = item["parameters"]
    base_num = params["base_num"]
    base_denom = params["base_denom"]
    multiplier = params.get("multiplier", 1)

    # The correct answer should be equivalent to base fraction
    correct = item["correct_answer"]

    if "/" in correct:
        # It's a fraction
        parts = correct.split("/")
        result_num = int(parts[0])
        result_denom = int(parts[1])

        frac1 = Fraction(base_num, base_denom)
        frac2 = Fraction(result_num, result_denom)

        if frac1 != frac2:
            return None  # Not equivalent

    return correct


def validate_item(item):
    """Validate a single item based on its question type and skill"""
    skill_id = item["skill_id"]

    try:
        if "compare" in skill_id:
            expected = validate_fraction_comparison(item)
        elif "add" in skill_id:
            expected = validate_fraction_addition(item)
        elif "equiv" in skill_id:
            expected = validate_equivalent_fraction(item)
        else:
            # Unknown type - skip validation
            return {"status": "skipped", "reason": "Unknown skill type"}

        if expected is None:
            return {"status": "invalid", "expected": "N/A", "actual": item["correct_answer"]}

        # Check equivalence for fractions
        if item.get("validation_rule") == "equivalent_fraction" and "/" in expected and "/" in item["correct_answer"]:
            expected_frac = Fraction(expected.split("/")[0], expected.split("/")[1])
            actual_frac = Fraction(item["correct_answer"].split("/")[0], item["correct_answer"].split("/")[1])

            if expected_frac == actual_frac:
                return {"status": "valid"}
            else:
                return {"status": "invalid", "expected": expected, "actual": item["correct_answer"]}

        # Exact match
        if expected == item["correct_answer"]:
            return {"status": "valid"}
        else:
            return {"status": "invalid", "expected": expected, "actual": item["correct_answer"]}

    except Exception as e:
        return {"status": "error", "error": str(e)}


def validate_content_pack():
    """Validate all items in content pack"""
    print("=" * 60)
    print("MathCoach Content Validator v0.1")
    print("=" * 60)
    print()

    with open('output/content_pack_v0.json') as f:
        items = json.load(f)

    print(f"Validating {len(items)} items...")
    print()

    invalid_items = []
    error_items = []
    skipped_items = []
    valid_count = 0

    for item in items:
        result = validate_item(item)

        if result["status"] == "valid":
            valid_count += 1
        elif result["status"] == "invalid":
            invalid_items.append({
                "item_id": item["item_id"],
                "skill_id": item["skill_id"],
                "expected": result.get("expected"),
                "actual": result.get("actual"),
                "parameters": item["parameters"]
            })
        elif result["status"] == "error":
            error_items.append({
                "item_id": item["item_id"],
                "error": result["error"]
            })
        elif result["status"] == "skipped":
            skipped_items.append({
                "item_id": item["item_id"],
                "reason": result["reason"]
            })

    # Print results
    print(f"✅ Valid items: {valid_count}/{len(items)}")

    if skipped_items:
        print(f"⏭️  Skipped: {len(skipped_items)} items")

    if error_items:
        print(f"\n⚠️  Errors: {len(error_items)} items")
        for err in error_items[:5]:  # Show first 5
            print(f"  {err['item_id']}: {err['error']}")

    if invalid_items:
        print(f"\n❌ Invalid items: {len(invalid_items)}")
        for inv in invalid_items[:10]:  # Show first 10
            print(f"  {inv['item_id']} ({inv['skill_id']})")
            print(f"    Expected: {inv['expected']}")
            print(f"    Actual: {inv['actual']}")
            print(f"    Params: {inv['parameters']}")
            print()

        # Save invalid items to file
        with open('output/invalid_items.json', 'w') as f:
            json.dump(invalid_items, f, indent=2)
        print(f"📝 Invalid items saved to output/invalid_items.json")
    else:
        print("\n🎉 All items validated successfully!")

    return len(invalid_items) == 0 and len(error_items) == 0


if __name__ == "__main__":
    success = validate_content_pack()
    exit(0 if success else 1)
