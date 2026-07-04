"""
Templates for decimal and percent skills.
"""
import random

from .base import deterministic_item_id


class DecimalTemplate:
    """Year 4 decimal place-value and comparison."""

    skill_id = "yr4_decimal_001"
    question_type = "numeric"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        mode = random.choice(["tenths", "hundredths", "compare"])

        if mode == "tenths":
            whole = random.randint(0, 20)
            tenths = random.randint(1, 9)
            value = whole + tenths / 10
            question = f"Write this decimal as a number: {whole} and {tenths} tenths"
            answer = f"{value:.1f}"
            explanation = f"{tenths} tenths is {tenths}/10 = 0.{tenths}. So the decimal is {answer}."
        elif mode == "hundredths":
            whole = random.randint(0, 20)
            hundredths = random.randint(1, 99)
            value = whole + hundredths / 100
            question = f"Write this decimal as a number: {whole} and {hundredths} hundredths"
            answer = f"{value:.2f}"
            explanation = f"{hundredths} hundredths is {hundredths}/100. So the decimal is {answer}."
        else:
            a = round(random.uniform(0.1, 9.9), 2)
            b = round(random.uniform(0.1, 9.9), 2)
            while abs(a - b) < 0.01:
                b = round(random.uniform(0.1, 9.9), 2)
            answer_val = max(a, b)
            question = f"Which is larger: {a:.2f} or {b:.2f}? Enter the number only."
            answer = f"{answer_val:.2f}"
            explanation = f"Compare whole numbers first, then tenths/hundredths. Larger value is {answer}."

        parameters = {"operation": "identity", "answer": answer, "mode": mode}
        item_id = deterministic_item_id(
            skill_id=DecimalTemplate.skill_id,
            difficulty=difficulty,
            parameters=parameters,
            question_text=question,
        )
        return {
            "item_id": item_id,
            "skill_id": DecimalTemplate.skill_id,
            "question_text": question,
            "question_type": DecimalTemplate.question_type,
            "difficulty": difficulty,
            "parameters": parameters,
            "correct_answer": answer,
            "hint": "Line up decimal places before comparing or converting.",
            "explanation": explanation,
            "validation_rule": "numeric",
        }


class PercentTemplate:
    """Year 5 percentage as fraction of 100."""

    skill_id = "yr5_percent_001"
    question_type = "numeric"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        mode = random.choice(["percent_of_100", "percent_of_multiple_10", "fraction_to_percent"])

        if mode == "percent_of_100":
            p = random.choice([5, 10, 20, 25, 30, 40, 50, 60, 75, 80, 90])
            question = f"What is {p}% of 100?"
            answer = p
            explanation = f"{p}% means {p} out of 100. So {p}% of 100 is {p}."
        elif mode == "percent_of_multiple_10":
            p = random.choice([10, 20, 25, 50, 75])
            base = random.choice([20, 40, 60, 80, 120, 200])
            answer = int(base * p / 100)
            question = f"What is {p}% of {base}?"
            explanation = f"{p}% of {base} = {base} × {p}/100 = {answer}."
        else:
            denom = random.choice([2, 4, 5, 10, 20, 25])
            num = random.randint(1, denom - 1)
            answer = int((num / denom) * 100)
            question = f"Convert {num}/{denom} to a percentage (number only)."
            explanation = f"{num}/{denom} = {answer}/100, so it is {answer}%."

        parameters = {"operation": "identity", "answer": answer, "mode": mode}
        item_id = deterministic_item_id(
            skill_id=PercentTemplate.skill_id,
            difficulty=difficulty,
            parameters=parameters,
            question_text=question,
        )
        return {
            "item_id": item_id,
            "skill_id": PercentTemplate.skill_id,
            "question_text": question,
            "question_type": PercentTemplate.question_type,
            "difficulty": difficulty,
            "parameters": parameters,
            "correct_answer": str(answer),
            "hint": "Percent means per 100.",
            "explanation": explanation,
            "validation_rule": "numeric",
        }


TEMPLATES = [
    DecimalTemplate,
    PercentTemplate,
]
