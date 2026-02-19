"""
Multiplication fact templates (times tables) for Year 3-4 learners.
"""
import random


class MultiplicationFactsTemplate:
    skill_id = "yr4_mult_div_001"
    question_type = "numeric"
    items_per_difficulty = 25  # 4 levels * 25 = 100 items total

    @staticmethod
    def generate(difficulty: int):
        if difficulty == 1:
            a = random.randint(2, 5)
            b = random.randint(1, 10)
            hint = "Use repeated addition or skip counting."
        elif difficulty == 2:
            a = random.randint(6, 9)
            b = random.randint(1, 10)
            hint = "Break it into easier chunks (e.g. 7×6 = 7×5 + 7)."
        elif difficulty == 3:
            a = random.randint(2, 12)
            b = random.randint(6, 12)
            hint = "Recall times-table patterns and commutative property."
        else:
            a = random.randint(11, 20)
            b = random.randint(2, 9)
            hint = "Split by place value: 14×6 = (10×6) + (4×6)."

        if random.choice([True, False]):
            a, b = b, a

        answer = a * b
        item_id = f"{MultiplicationFactsTemplate.skill_id}_d{difficulty}_{random.randint(1000, 9999)}"

        return {
            "item_id": item_id,
            "skill_id": MultiplicationFactsTemplate.skill_id,
            "question_text": f"What is {a} × {b}?",
            "question_type": MultiplicationFactsTemplate.question_type,
            "difficulty": difficulty,
            "parameters": {"a": a, "b": b},
            "correct_answer": str(answer),
            "hint": hint,
            "explanation": f"{a} × {b} = {answer}",
            "validation_rule": "numeric",
        }


TEMPLATES = [MultiplicationFactsTemplate]
