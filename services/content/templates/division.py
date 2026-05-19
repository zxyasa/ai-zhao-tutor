"""
Templates for multiplication/division and ratio skills.
"""
import math
import random
import uuid


class MultiplicationDivisionTemplate:
    """Year 4 multiplication/division within 100."""

    skill_id = "yr4_mult_div_001"
    question_type = "numeric"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        op = random.choice(["mul", "div"])

        if difficulty == 1:
            a = random.randint(2, 9)
            b = random.randint(2, 9)
        elif difficulty == 2:
            a = random.randint(4, 12)
            b = random.randint(2, 12)
        elif difficulty == 3:
            a = random.randint(6, 15)
            b = random.randint(3, 12)
        else:
            a = random.randint(8, 20)
            b = random.randint(4, 12)

        if op == "mul":
            answer = a * b
            question = f"What is {a} × {b}?"
            hint = "Break into easier parts if needed."
            explanation = f"{a} × {b} = {answer}."
        else:
            product = a * b
            answer = a
            question = f"What is {product} ÷ {b}?"
            hint = "Think of the related multiplication fact."
            explanation = f"Because {a} × {b} = {product}, {product} ÷ {b} = {a}."

        item_id = f"{MultiplicationDivisionTemplate.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": MultiplicationDivisionTemplate.skill_id,
            "question_text": question,
            "question_type": MultiplicationDivisionTemplate.question_type,
            "difficulty": difficulty,
            "parameters": {"operation": op, "a": a, "b": b},
            "correct_answer": str(answer),
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "numeric",
        }


class RatioTemplate:
    """Year 6 ratio simplification and scaling."""

    skill_id = "yr6_ratio_001"
    question_type = "numeric"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        mode = random.choice(["simplify_left", "simplify_right", "scale_up"])

        if mode in {"simplify_left", "simplify_right"}:
            base_a = random.randint(1, 9 + difficulty)
            base_b = random.randint(1, 9 + difficulty)
            while math.gcd(base_a, base_b) != 1:
                base_a = random.randint(1, 9 + difficulty)
                base_b = random.randint(1, 9 + difficulty)

            factor = random.randint(2, 6)
            a = base_a * factor
            b = base_b * factor

            if mode == "simplify_left":
                question = f"Simplify the ratio {a}:{b}. Fill the first number: ?:{base_b}"
                answer = base_a
                explanation = f"{a}:{b} ÷ {factor} = {base_a}:{base_b}."
            else:
                question = f"Simplify the ratio {a}:{b}. Fill the second number: {base_a}:?"
                answer = base_b
                explanation = f"{a}:{b} ÷ {factor} = {base_a}:{base_b}."
        else:
            a = random.randint(2, 10)
            b = random.randint(2, 10)
            factor = random.randint(2, 6)
            question = f"If the ratio is {a}:{b}, what is the first number when the second is {b * factor}?"
            answer = a * factor
            explanation = f"Scale both parts by {factor}: {a}:{b} -> {a * factor}:{b * factor}."

        item_id = f"{RatioTemplate.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": RatioTemplate.skill_id,
            "question_text": question,
            "question_type": RatioTemplate.question_type,
            "difficulty": difficulty,
            "parameters": {"operation": "identity", "answer": answer, "mode": mode},
            "correct_answer": str(answer),
            "hint": "Ratios scale by multiplying or dividing both parts by the same number.",
            "explanation": explanation,
            "validation_rule": "numeric",
        }


TEMPLATES = [
    MultiplicationDivisionTemplate,
    RatioTemplate,
]
