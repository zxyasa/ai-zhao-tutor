"""
Validate generated items by recomputing expected answers from parameters.
"""
import json
from fractions import Fraction


def _to_fraction(value: str) -> Fraction:
    if "/" in value:
        n, d = value.split("/", 1)
        return Fraction(int(n), int(d))
    return Fraction(value)


def _normalize_answer(value) -> str:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    return str(value)


def expected_answer(item: dict):
    p = item.get("parameters", {})
    op = p.get("operation")
    skill_id = item.get("skill_id", "")

    # Generic arithmetic operations used by numeric templates.
    if op == "add":
        return p["a"] + p["b"]
    if op == "sub":
        return p["a"] - p["b"]
    if op == "mul":
        return p["a"] * p["b"]
    if op == "div":
        return p["a"]

    # Identity type templates store direct expected answer.
    if op == "identity":
        if "answer" in p:
            return p["answer"]
        if "x" in p:
            return p["x"]
        if "num" in p and "denom" in p:
            return Fraction(p["num"], p["denom"])

    # Fraction operations.
    if op == "max_fraction":
        f1 = Fraction(p["num1"], p["denom1"])
        f2 = Fraction(p["num2"], p["denom2"])
        return f1 if f1 > f2 else f2
    if op == "equivalent":
        # Accept any equivalent answer, fallback expected uses multiplied form.
        return Fraction(p["num"], p["denom"])
    if op == "simplify":
        return Fraction(p["num"], p["denom"])
    if op == "add_frac":
        return Fraction(p["num1"], p["denom1"]) + Fraction(p["num2"], p["denom2"])
    if op == "sub_frac":
        return Fraction(p["num1"], p["denom1"]) - Fraction(p["num2"], p["denom2"])
    if op == "mul_frac":
        return Fraction(p["num1"], p["denom1"]) * Fraction(p["num2"], p["denom2"])
    if op == "div_frac":
        return Fraction(p["num1"], p["denom1"]) / Fraction(p["num2"], p["denom2"])
    if op == "to_improper":
        return Fraction(p["whole"] * p["denom"] + p["num"], p["denom"])
    if op == "to_mixed_num_only":
        return p["improper_num"] % p["denom"]

    # Backward compatibility with legacy fraction templates.
    if {"a", "b"}.issubset(p.keys()) and skill_id == "yr4_mult_div_001":
        return p["a"] * p["b"]
    if "compare" in skill_id and {"num1", "num2", "denom1", "denom2"}.issubset(p.keys()):
        f1 = Fraction(p["num1"], p["denom1"])
        f2 = Fraction(p["num2"], p["denom2"])
        return f1 if f1 > f2 else f2
    if "equiv" in skill_id and {"base_num", "base_denom"}.issubset(p.keys()):
        return Fraction(p["base_num"], p["base_denom"])
    if "add" in skill_id and {"num1", "num2", "denom1", "denom2"}.issubset(p.keys()):
        return Fraction(p["num1"], p["denom1"]) + Fraction(p["num2"], p["denom2"])

    return None


def validate_item(item: dict) -> dict:
    expected = expected_answer(item)
    if expected is None:
        return {"status": "skipped", "reason": "Unknown schema"}

    actual_raw = item.get("correct_answer", "")
    rule = item.get("validation_rule", "")

    try:
        if rule in {"fraction", "equivalent_fraction"} or isinstance(expected, Fraction):
            expected_frac = expected if isinstance(expected, Fraction) else _to_fraction(str(expected))
            actual_frac = _to_fraction(str(actual_raw))
            if expected_frac == actual_frac:
                return {"status": "valid"}
            return {
                "status": "invalid",
                "expected": _normalize_answer(expected_frac),
                "actual": str(actual_raw),
            }

        if rule in {"numeric", "exact_match"}:
            exp_val = float(expected)
            act_val = float(actual_raw)
            if abs(exp_val - act_val) < 1e-6:
                return {"status": "valid"}
            return {"status": "invalid", "expected": str(expected), "actual": str(actual_raw)}

        # Default exact string compare.
        if str(expected) == str(actual_raw):
            return {"status": "valid"}
        return {"status": "invalid", "expected": str(expected), "actual": str(actual_raw)}

    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def validate_content_pack() -> bool:
    print("=" * 60)
    print("MathCoach Content Validator v0.2")
    print("=" * 60)
    print()

    with open("output/content_pack_v0.json", encoding="utf-8") as f:
        items = json.load(f)

    print(f"Validating {len(items)} items...\n")

    invalid_items = []
    error_items = []
    skipped_items = []
    valid_count = 0

    for item in items:
        result = validate_item(item)
        if result["status"] == "valid":
            valid_count += 1
        elif result["status"] == "invalid":
            invalid_items.append(
                {
                    "item_id": item["item_id"],
                    "skill_id": item["skill_id"],
                    "expected": result.get("expected"),
                    "actual": result.get("actual"),
                    "parameters": item.get("parameters", {}),
                }
            )
        elif result["status"] == "error":
            error_items.append({"item_id": item["item_id"], "error": result["error"]})
        else:
            skipped_items.append({"item_id": item["item_id"], "reason": result["reason"]})

    print(f"✅ Valid items: {valid_count}/{len(items)}")
    if skipped_items:
        print(f"⏭️  Skipped: {len(skipped_items)}")
    if error_items:
        print(f"⚠️  Errors: {len(error_items)}")
        for err in error_items[:5]:
            print(f"  {err['item_id']}: {err['error']}")
    if invalid_items:
        print(f"❌ Invalid items: {len(invalid_items)}")
        for inv in invalid_items[:10]:
            print(f"  {inv['item_id']} ({inv['skill_id']}): expected {inv['expected']} actual {inv['actual']}")
        with open("output/invalid_items.json", "w", encoding="utf-8") as f:
            json.dump(invalid_items, f, indent=2)
        print("📝 Invalid items saved to output/invalid_items.json")
    else:
        print("\n🎉 All items validated successfully!")

    return len(invalid_items) == 0 and len(error_items) == 0


if __name__ == "__main__":
    success = validate_content_pack()
    raise SystemExit(0 if success else 1)
