"""
Fraction templates with deterministic-style generation and explicit parameters for validation.
"""
import math
import random
import uuid
from fractions import Fraction


def _rand_fraction(min_denom: int = 2, max_denom: int = 12) -> tuple[int, int]:
    denom = random.randint(min_denom, max_denom)
    num = random.randint(1, denom - 1)
    return num, denom


def _format_fraction(frac: Fraction) -> str:
    return f"{frac.numerator}/{frac.denominator}"


class FractionIntroTemplate:
    skill_id = "yr3_frac_intro_001"
    question_type = "fraction"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        total = random.randint(4, 8 + difficulty * 2)
        shaded = random.randint(1, total - 1)
        answer = f"{shaded}/{total}"
        item_id = f"{FractionIntroTemplate.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": FractionIntroTemplate.skill_id,
            "question_text": f"A shape is split into {total} equal parts and {shaded} are shaded. Write the fraction shaded.",
            "question_type": FractionIntroTemplate.question_type,
            "difficulty": difficulty,
            "parameters": {"operation": "identity", "num": shaded, "denom": total},
            "correct_answer": answer,
            "hint": "Fraction = shaded parts / total equal parts.",
            "explanation": f"Shaded {shaded} out of {total}, so the fraction is {answer}.",
            "validation_rule": "fraction",
        }


class FractionComparisonTemplate:
    skill_id = "yr3_frac_compare_001"
    question_type = "fraction"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        if difficulty <= 2:
            denom = random.randint(3, 12 + difficulty * 3)
            n1 = random.randint(1, denom - 1)
            n2 = random.randint(1, denom - 1)
            while n1 == n2:
                n2 = random.randint(1, denom - 1)
            left = Fraction(n1, denom)
            right = Fraction(n2, denom)
            d1, d2 = denom, denom
        else:
            n1, d1 = _rand_fraction(3, 10 + difficulty * 2)
            n2, d2 = _rand_fraction(3, 10 + difficulty * 2)
            left = Fraction(n1, d1)
            right = Fraction(n2, d2)
            while left == right:
                n2, d2 = _rand_fraction(3, 10 + difficulty * 2)
                right = Fraction(n2, d2)

        answer = f"{n1}/{d1}" if left > right else f"{n2}/{d2}"
        item_id = f"{FractionComparisonTemplate.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": FractionComparisonTemplate.skill_id,
            "question_text": f"Which is larger: {n1}/{d1} or {n2}/{d2}?",
            "question_type": FractionComparisonTemplate.question_type,
            "difficulty": difficulty,
            "parameters": {"operation": "max_fraction", "num1": n1, "denom1": d1, "num2": n2, "denom2": d2},
            "correct_answer": answer,
            "hint": "Use a common denominator when needed.",
            "explanation": "Convert to a common denominator and compare numerators.",
            "validation_rule": "fraction",
        }


class FractionIdentifyTemplate:
    skill_id = "yr3_frac_identify_001"
    question_type = "fraction"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        total = random.randint(3, 10 + difficulty * 2)
        shaded = random.randint(1, total - 1)
        answer = f"{shaded}/{total}"
        item_id = f"{FractionIdentifyTemplate.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": FractionIdentifyTemplate.skill_id,
            "question_text": f"Out of {total} equal parts, {shaded} are highlighted. What fraction is highlighted?",
            "question_type": FractionIdentifyTemplate.question_type,
            "difficulty": difficulty,
            "parameters": {"operation": "identity", "num": shaded, "denom": total},
            "correct_answer": answer,
            "hint": "Write highlighted over total parts.",
            "explanation": f"That is {shaded}/{total}.",
            "validation_rule": "fraction",
        }


class EquivalentFractionTemplate:
    skill_id = "yr4_frac_equiv_001"
    question_type = "fraction"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        num, denom = _rand_fraction(2, 9)
        factor = random.randint(2, 2 + difficulty)

        if difficulty <= 3:
            target_denom = denom * factor
            answer = f"{num * factor}/{target_denom}"
            q = f"Find an equivalent fraction to {num}/{denom} with denominator {target_denom}."
        else:
            uns_num = num * factor
            uns_den = denom * factor
            answer = f"{num}/{denom}"
            q = f"Simplify {uns_num}/{uns_den} to lowest terms."

        item_id = f"{EquivalentFractionTemplate.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": EquivalentFractionTemplate.skill_id,
            "question_text": q,
            "question_type": EquivalentFractionTemplate.question_type,
            "difficulty": difficulty,
            "parameters": {"operation": "equivalent", "num": num, "denom": denom, "factor": factor},
            "correct_answer": answer,
            "hint": "Multiply or divide numerator and denominator by the same number.",
            "explanation": "Equivalent fractions keep the same value.",
            "validation_rule": "fraction",
        }


class FractionCompareAdvancedTemplate:
    skill_id = "yr4_frac_compare_002"
    question_type = "fraction"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        n1, d1 = _rand_fraction(3, 12 + difficulty * 2)
        n2, d2 = _rand_fraction(3, 12 + difficulty * 2)
        left = Fraction(n1, d1)
        right = Fraction(n2, d2)
        while left == right:
            n2, d2 = _rand_fraction(3, 12 + difficulty * 2)
            right = Fraction(n2, d2)

        answer = f"{n1}/{d1}" if left > right else f"{n2}/{d2}"
        item_id = f"{FractionCompareAdvancedTemplate.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": FractionCompareAdvancedTemplate.skill_id,
            "question_text": f"Which is larger: {n1}/{d1} or {n2}/{d2}?",
            "question_type": FractionCompareAdvancedTemplate.question_type,
            "difficulty": difficulty,
            "parameters": {"operation": "max_fraction", "num1": n1, "denom1": d1, "num2": n2, "denom2": d2},
            "correct_answer": answer,
            "hint": "Use LCM/common denominator.",
            "explanation": "Convert to common denominator and compare.",
            "validation_rule": "fraction",
        }


class FractionSimplifyTemplate:
    skill_id = "yr4_frac_simplify_001"
    question_type = "fraction"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        base_n, base_d = _rand_fraction(2, 10)
        factor = random.randint(2, 4 + difficulty)
        n = base_n * factor
        d = base_d * factor
        answer = f"{base_n}/{base_d}"
        item_id = f"{FractionSimplifyTemplate.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": FractionSimplifyTemplate.skill_id,
            "question_text": f"Simplify {n}/{d} to lowest terms.",
            "question_type": FractionSimplifyTemplate.question_type,
            "difficulty": difficulty,
            "parameters": {"operation": "simplify", "num": n, "denom": d},
            "correct_answer": answer,
            "hint": "Divide numerator and denominator by the GCD.",
            "explanation": f"GCD({n}, {d}) = {factor}.",
            "validation_rule": "fraction",
        }


class FractionAdditionTemplate:
    skill_id = "yr5_frac_add_001"
    question_type = "fraction"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        denom = random.randint(3, 10 + difficulty)
        n1 = random.randint(1, denom - 1)
        n2 = random.randint(1, denom - 1)
        result = Fraction(n1, denom) + Fraction(n2, denom)
        answer = _format_fraction(result)
        item_id = f"{FractionAdditionTemplate.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": FractionAdditionTemplate.skill_id,
            "question_text": f"What is {n1}/{denom} + {n2}/{denom}?",
            "question_type": FractionAdditionTemplate.question_type,
            "difficulty": difficulty,
            "parameters": {"operation": "add_frac", "num1": n1, "denom1": denom, "num2": n2, "denom2": denom},
            "correct_answer": answer,
            "hint": "Same denominator: add numerators.",
            "explanation": "Then simplify if needed.",
            "validation_rule": "fraction",
        }


class FractionAdditionDiffTemplate:
    skill_id = "yr5_frac_add_002"
    question_type = "fraction"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        n1, d1 = _rand_fraction(2, 8 + difficulty)
        n2, d2 = _rand_fraction(2, 8 + difficulty)
        result = Fraction(n1, d1) + Fraction(n2, d2)
        answer = _format_fraction(result)
        item_id = f"{FractionAdditionDiffTemplate.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": FractionAdditionDiffTemplate.skill_id,
            "question_text": f"What is {n1}/{d1} + {n2}/{d2}?",
            "question_type": FractionAdditionDiffTemplate.question_type,
            "difficulty": difficulty,
            "parameters": {"operation": "add_frac", "num1": n1, "denom1": d1, "num2": n2, "denom2": d2},
            "correct_answer": answer,
            "hint": "Use a common denominator.",
            "explanation": "Add converted numerators and simplify.",
            "validation_rule": "fraction",
        }


class FractionSubtractionTemplate:
    skill_id = "yr5_frac_sub_001"
    question_type = "fraction"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        denom = random.randint(3, 10 + difficulty)
        n1 = random.randint(2, denom)
        n2 = random.randint(1, n1 - 1)
        result = Fraction(n1, denom) - Fraction(n2, denom)
        answer = _format_fraction(result)
        item_id = f"{FractionSubtractionTemplate.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": FractionSubtractionTemplate.skill_id,
            "question_text": f"What is {n1}/{denom} - {n2}/{denom}?",
            "question_type": FractionSubtractionTemplate.question_type,
            "difficulty": difficulty,
            "parameters": {"operation": "sub_frac", "num1": n1, "denom1": denom, "num2": n2, "denom2": denom},
            "correct_answer": answer,
            "hint": "Same denominator: subtract numerators.",
            "explanation": "Then simplify if possible.",
            "validation_rule": "fraction",
        }


class FractionSubtractionDiffTemplate:
    skill_id = "yr5_frac_sub_002"
    question_type = "fraction"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        n1, d1 = _rand_fraction(2, 8 + difficulty)
        n2, d2 = _rand_fraction(2, 8 + difficulty)
        while Fraction(n1, d1) <= Fraction(n2, d2):
            n1, d1 = _rand_fraction(2, 8 + difficulty)
            n2, d2 = _rand_fraction(2, 8 + difficulty)
        result = Fraction(n1, d1) - Fraction(n2, d2)
        answer = _format_fraction(result)
        item_id = f"{FractionSubtractionDiffTemplate.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": FractionSubtractionDiffTemplate.skill_id,
            "question_text": f"What is {n1}/{d1} - {n2}/{d2}?",
            "question_type": FractionSubtractionDiffTemplate.question_type,
            "difficulty": difficulty,
            "parameters": {"operation": "sub_frac", "num1": n1, "denom1": d1, "num2": n2, "denom2": d2},
            "correct_answer": answer,
            "hint": "Convert to a common denominator first.",
            "explanation": "Subtract converted numerators and simplify.",
            "validation_rule": "fraction",
        }


class FractionMultiplyTemplate:
    skill_id = "yr6_frac_mult_001"
    question_type = "fraction"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        n1, d1 = _rand_fraction(2, 8 + difficulty)
        n2, d2 = _rand_fraction(2, 8 + difficulty)
        result = Fraction(n1, d1) * Fraction(n2, d2)
        answer = _format_fraction(result)
        item_id = f"{FractionMultiplyTemplate.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": FractionMultiplyTemplate.skill_id,
            "question_text": f"What is {n1}/{d1} × {n2}/{d2}?",
            "question_type": FractionMultiplyTemplate.question_type,
            "difficulty": difficulty,
            "parameters": {"operation": "mul_frac", "num1": n1, "denom1": d1, "num2": n2, "denom2": d2},
            "correct_answer": answer,
            "hint": "Multiply numerators, multiply denominators.",
            "explanation": "Simplify final answer.",
            "validation_rule": "fraction",
        }


class FractionDivideTemplate:
    skill_id = "yr6_frac_div_001"
    question_type = "fraction"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        n1, d1 = _rand_fraction(2, 8 + difficulty)
        n2, d2 = _rand_fraction(2, 8 + difficulty)
        result = Fraction(n1, d1) / Fraction(n2, d2)
        answer = _format_fraction(result)
        item_id = f"{FractionDivideTemplate.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": FractionDivideTemplate.skill_id,
            "question_text": f"What is {n1}/{d1} ÷ {n2}/{d2}?",
            "question_type": FractionDivideTemplate.question_type,
            "difficulty": difficulty,
            "parameters": {"operation": "div_frac", "num1": n1, "denom1": d1, "num2": n2, "denom2": d2},
            "correct_answer": answer,
            "hint": "Multiply by the reciprocal of the second fraction.",
            "explanation": "Invert second fraction, then multiply.",
            "validation_rule": "fraction",
        }


class FractionMixedTemplate:
    skill_id = "yr6_frac_mixed_001"
    question_type = "fraction"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        mode = random.choice(["to_improper", "to_mixed"])

        whole = random.randint(1, 6 + difficulty)
        frac_num = random.randint(1, 7)
        frac_denom = random.randint(frac_num + 1, 12)

        if mode == "to_improper":
            improper = Fraction(whole * frac_denom + frac_num, frac_denom)
            answer = _format_fraction(improper)
            question = f"Convert {whole} {frac_num}/{frac_denom} to an improper fraction."
            parameters = {"operation": "to_improper", "whole": whole, "num": frac_num, "denom": frac_denom}
            rule = "fraction"
        else:
            num = whole * frac_denom + frac_num
            question = f"Convert {num}/{frac_denom} to a mixed number. Enter only the numerator of the fractional part. {whole} ?/{frac_denom}"
            answer = str(frac_num)
            parameters = {"operation": "to_mixed_num_only", "improper_num": num, "denom": frac_denom, "whole": whole}
            rule = "numeric"

        item_id = f"{FractionMixedTemplate.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": FractionMixedTemplate.skill_id,
            "question_text": question,
            "question_type": FractionMixedTemplate.question_type,
            "difficulty": difficulty,
            "parameters": parameters,
            "correct_answer": answer,
            "hint": "Use whole × denominator + numerator for improper conversion.",
            "explanation": "Mixed and improper fractions represent the same value.",
            "validation_rule": rule,
        }


TEMPLATES = [
    FractionIntroTemplate,
    FractionComparisonTemplate,
    FractionIdentifyTemplate,
    EquivalentFractionTemplate,
    FractionCompareAdvancedTemplate,
    FractionSimplifyTemplate,
    FractionAdditionTemplate,
    FractionAdditionDiffTemplate,
    FractionSubtractionTemplate,
    FractionSubtractionDiffTemplate,
    FractionMultiplyTemplate,
    FractionDivideTemplate,
    FractionMixedTemplate,
]


def get_templates_for_skill(skill_id):
    return [t for t in TEMPLATES if t.skill_id == skill_id]
