"""
Fraction item templates with deterministic generation and validation
"""
import random
from fractions import Fraction as FractionCalc
import math


class FractionComparisonTemplate:
    """Compare two fractions - which is larger?"""
    skill_id = "yr3_frac_compare_001"
    question_type = "fraction"

    @staticmethod
    def generate(difficulty: int):
        """
        Difficulty scaling:
        1: Same denominator, denominators ≤ 10
        2: Same denominator, denominators ≤ 20
        3: Different denominators, both ≤ 10, one is multiple of other
        4: Different denominators, both ≤ 12
        5: Different denominators, requires LCM, up to 20
        """
        if difficulty == 1:
            denom = random.randint(3, 10)
            num1 = random.randint(1, denom - 1)
            num2 = random.randint(1, denom - 1)
            while num1 == num2:
                num2 = random.randint(1, denom - 1)

            correct = f"{max(num1, num2)}/{denom}"
            hint = "When denominators are the same, compare the numerators"
            explanation = f"Since both fractions have denominator {denom}, we compare numerators: {max(num1, num2)} > {min(num1, num2)}, so {max(num1, num2)}/{denom} is larger"

        elif difficulty == 2:
            denom = random.randint(3, 20)
            num1 = random.randint(1, denom - 1)
            num2 = random.randint(1, denom - 1)
            while num1 == num2:
                num2 = random.randint(1, denom - 1)

            correct = f"{max(num1, num2)}/{denom}"
            hint = "When denominators are the same, which numerator is larger?"
            explanation = f"Both fractions have denominator {denom}. Compare numerators: {max(num1, num2)} > {min(num1, num2)}"

        else:  # difficulty 3-5: different denominators
            if difficulty == 3:
                denom1 = random.randint(2, 5)
                denom2 = denom1 * random.randint(2, 3)
            elif difficulty == 4:
                denom1 = random.randint(2, 12)
                denom2 = random.randint(2, 12)
                while denom2 == denom1:
                    denom2 = random.randint(2, 12)
            else:  # 5
                denom1 = random.randint(2, 20)
                denom2 = random.randint(2, 20)
                while denom2 == denom1:
                    denom2 = random.randint(2, 20)

            num1 = random.randint(1, denom1 - 1)
            num2 = random.randint(1, denom2 - 1)

            # Use fractions library for correct comparison
            frac1 = FractionCalc(num1, denom1)
            frac2 = FractionCalc(num2, denom2)

            if frac1 == frac2:
                num2 = num2 + 1 if num2 < denom2 - 1 else num2 - 1
                frac2 = FractionCalc(num2, denom2)

            correct = f"{num1}/{denom1}" if frac1 > frac2 else f"{num2}/{denom2}"
            hint = "Find a common denominator to compare fractions with different denominators"
            lcm = (denom1 * denom2) // math.gcd(denom1, denom2)
            explanation = f"Convert to common denominator {lcm}: {num1}/{denom1} = {num1 * (lcm // denom1)}/{lcm} and {num2}/{denom2} = {num2 * (lcm // denom2)}/{lcm}. Then compare numerators."

        item_id = f"{FractionComparisonTemplate.skill_id}_d{difficulty}_{random.randint(1000, 9999)}"

        return {
            "item_id": item_id,
            "skill_id": FractionComparisonTemplate.skill_id,
            "question_text": f"Which is larger: {num1}/{denom if difficulty <= 2 else denom1} or {num2}/{denom if difficulty <= 2 else denom2}?",
            "question_type": FractionComparisonTemplate.question_type,
            "difficulty": difficulty,
            "parameters": {
                "num1": num1,
                "num2": num2,
                "denom1": denom if difficulty <= 2 else denom1,
                "denom2": denom if difficulty <= 2 else denom2
            },
            "correct_answer": correct,
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "exact_match"
        }


class FractionAdditionTemplate:
    """Add two fractions"""
    skill_id = "yr5_frac_add_001"
    question_type = "fraction"

    @staticmethod
    def generate(difficulty: int):
        """
        Difficulty scaling:
        1: Same denominator ≤ 10, sum < 1
        2: Same denominator ≤ 10, sum may be improper
        3: Different denominators, one multiple of other
        4: Different denominators, need LCM
        5: Different denominators, result needs simplification
        """
        if difficulty <= 2:
            denom = random.randint(2, 10)
            if difficulty == 1:
                num1 = random.randint(1, denom - 2)
                num2 = random.randint(1, denom - num1 - 1)
            else:
                num1 = random.randint(1, denom - 1)
                num2 = random.randint(1, denom - 1)

            result_num = num1 + num2
            result_denom = denom

            hint = "When denominators are the same, add the numerators and keep the denominator"
            explanation = f"Since both fractions have denominator {denom}, add numerators: {num1} + {num2} = {result_num}. Answer: {result_num}/{result_denom}"

        else:  # different denominators
            if difficulty == 3:
                denom1 = random.randint(2, 5)
                denom2 = denom1 * random.randint(2, 3)
            else:
                denom1 = random.randint(2, 12)
                denom2 = random.randint(2, 12)
                while denom2 == denom1:
                    denom2 = random.randint(2, 12)

            num1 = random.randint(1, denom1 - 1)
            num2 = random.randint(1, denom2 - 1)

            # Calculate using fractions library
            frac_result = FractionCalc(num1, denom1) + FractionCalc(num2, denom2)

            if difficulty == 5:
                # Keep in simplified form
                result_num = frac_result.numerator
                result_denom = frac_result.denominator
            else:
                # Use common denominator
                lcm = (denom1 * denom2) // math.gcd(denom1, denom2)
                result_num = num1 * (lcm // denom1) + num2 * (lcm // denom2)
                result_denom = lcm

            hint = "Find a common denominator, then add the numerators"
            explanation = f"Common denominator is {result_denom}. Convert and add: ({num1 * (result_denom // denom1)} + {num2 * (result_denom // denom2)}) / {result_denom} = {result_num}/{result_denom}"

        correct_answer = f"{result_num}/{result_denom}"
        item_id = f"{FractionAdditionTemplate.skill_id}_d{difficulty}_{random.randint(1000, 9999)}"

        return {
            "item_id": item_id,
            "skill_id": FractionAdditionTemplate.skill_id,
            "question_text": f"What is {num1}/{denom if difficulty <= 2 else denom1} + {num2}/{denom if difficulty <= 2 else denom2}?",
            "question_type": FractionAdditionTemplate.question_type,
            "difficulty": difficulty,
            "parameters": {
                "num1": num1,
                "num2": num2,
                "denom1": denom if difficulty <= 2 else denom1,
                "denom2": denom if difficulty <= 2 else denom2,
                "result_num": result_num,
                "result_denom": result_denom
            },
            "correct_answer": correct_answer,
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "equivalent_fraction"
        }


class EquivalentFractionTemplate:
    """Find equivalent fraction"""
    skill_id = "yr4_frac_equiv_001"
    question_type = "fraction"

    @staticmethod
    def generate(difficulty: int):
        """
        Difficulty scaling:
        1: Multiply numerator and denominator by 2
        2: Multiply by 3 or 4
        3: Multiply by values up to 6
        4: Find missing numerator or denominator
        5: Simplify to lowest terms
        """
        base_denom = random.randint(2, 8)
        base_num = random.randint(1, base_denom - 1)

        if difficulty <= 3:
            multiplier = 2 if difficulty == 1 else (random.randint(2, 3) if difficulty == 2 else random.randint(2, 6))
            target_num = base_num * multiplier
            target_denom = base_denom * multiplier

            question = f"What is an equivalent fraction to {base_num}/{base_denom}? (Use denominator {target_denom})"
            correct = f"{target_num}/{target_denom}"
            hint = "Multiply both numerator and denominator by the same number"
            explanation = f"To get denominator {target_denom}, multiply {base_denom} by {multiplier}. Also multiply numerator: {base_num} × {multiplier} = {target_num}"

        elif difficulty == 4:
            multiplier = random.randint(2, 5)
            if random.choice([True, False]):
                # Missing numerator
                target_denom = base_denom * multiplier
                target_num = base_num * multiplier
                question = f"Find the missing numerator: {base_num}/{base_denom} = ?/{target_denom}"
                correct = str(target_num)
            else:
                # Missing denominator
                target_num = base_num * multiplier
                target_denom = base_denom * multiplier
                question = f"Find the missing denominator: {base_num}/{base_denom} = {target_num}/?"
                correct = str(target_denom)

            hint = "What number do you multiply the known values by?"
            explanation = f"Multiply both parts by {multiplier}"

        else:  # difficulty == 5: simplify
            multiplier = random.randint(2, 6)
            unsimplified_num = base_num * multiplier
            unsimplified_denom = base_denom * multiplier

            question = f"Simplify {unsimplified_num}/{unsimplified_denom} to lowest terms"
            correct = f"{base_num}/{base_denom}"
            hint = "Find the greatest common divisor and divide both numerator and denominator by it"
            explanation = f"GCD of {unsimplified_num} and {unsimplified_denom} is {multiplier}. Divide both: {unsimplified_num}÷{multiplier} = {base_num}, {unsimplified_denom}÷{multiplier} = {base_denom}"

        item_id = f"{EquivalentFractionTemplate.skill_id}_d{difficulty}_{random.randint(1000, 9999)}"

        return {
            "item_id": item_id,
            "skill_id": EquivalentFractionTemplate.skill_id,
            "question_text": question,
            "question_type": EquivalentFractionTemplate.question_type,
            "difficulty": difficulty,
            "parameters": {
                "base_num": base_num,
                "base_denom": base_denom,
                "multiplier": multiplier
            },
            "correct_answer": correct,
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "equivalent_fraction" if "/" in correct else "exact_match"
        }


# Template registry
TEMPLATES = [
    FractionComparisonTemplate,
    FractionAdditionTemplate,
    EquivalentFractionTemplate
]


def get_templates_for_skill(skill_id):
    """Get all templates for a specific skill"""
    return [t for t in TEMPLATES if t.skill_id == skill_id]
