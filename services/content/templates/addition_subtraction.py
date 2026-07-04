"""
Templates for place value, arithmetic, and intro algebra skills.
"""
import random

from .base import deterministic_item_id


class PlaceValueTemplate:
    """Year 3 place value to hundreds."""

    skill_id = "yr3_num_place_001"
    question_type = "numeric"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        n = random.randint(100, 999 if difficulty >= 2 else 499)
        mode = random.choice(["hundreds", "tens", "ones", "expand"])

        if mode == "hundreds":
            answer = n // 100
            question = f"How many hundreds are in {n}?"
            hint = "The hundreds digit is the first digit."
            explanation = f"{n} has {answer} hundreds."
        elif mode == "tens":
            answer = (n // 10) % 10
            question = f"What is the tens digit in {n}?"
            hint = "The tens digit is the middle digit."
            explanation = f"In {n}, the tens digit is {answer}."
        elif mode == "ones":
            answer = n % 10
            question = f"What is the ones digit in {n}?"
            hint = "The ones digit is the rightmost digit."
            explanation = f"In {n}, the ones digit is {answer}."
        else:
            h = n // 100
            t = (n // 10) % 10
            o = n % 10
            answer = h * 100 + t * 10 + o
            question = f"Write in digits: {h * 100} + {t * 10} + {o}"
            hint = "Combine hundreds, tens, and ones."
            explanation = f"{h * 100} + {t * 10} + {o} = {answer}."

        parameters = {"operation": "identity", "number": n, "mode": mode, "answer": answer}
        item_id = deterministic_item_id(
            skill_id=PlaceValueTemplate.skill_id,
            difficulty=difficulty,
            parameters=parameters,
            question_text=question,
        )
        return {
            "item_id": item_id,
            "skill_id": PlaceValueTemplate.skill_id,
            "question_text": question,
            "question_type": PlaceValueTemplate.question_type,
            "difficulty": difficulty,
            "parameters": parameters,
            "correct_answer": str(answer),
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "numeric",
        }


class AdditionSubtractionTemplate:
    """Year 3 add/subtract within 1000."""

    skill_id = "yr3_add_sub_001"
    question_type = "numeric"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        op = random.choice(["add", "sub"])

        if difficulty == 1:
            a = random.randint(10, 99)
            b = random.randint(1, 30)
        elif difficulty == 2:
            a = random.randint(100, 399)
            b = random.randint(10, 99)
        elif difficulty == 3:
            a = random.randint(200, 799)
            b = random.randint(20, 199)
        else:
            a = random.randint(300, 999)
            b = random.randint(50, 299)

        if op == "add":
            answer = a + b
            question = f"What is {a} + {b}?"
            hint = "Line up place values before adding."
            explanation = f"{a} + {b} = {answer}."
        else:
            if b > a:
                a, b = b, a
            answer = a - b
            question = f"What is {a} - {b}?"
            hint = "Subtract ones, tens, and hundreds in order."
            explanation = f"{a} - {b} = {answer}."

        parameters = {"operation": op, "a": a, "b": b}
        item_id = deterministic_item_id(
            skill_id=AdditionSubtractionTemplate.skill_id,
            difficulty=difficulty,
            parameters=parameters,
            question_text=question,
        )
        return {
            "item_id": item_id,
            "skill_id": AdditionSubtractionTemplate.skill_id,
            "question_text": question,
            "question_type": AdditionSubtractionTemplate.question_type,
            "difficulty": difficulty,
            "parameters": parameters,
            "correct_answer": str(answer),
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "numeric",
        }


class AlgebraIntroTemplate:
    """Year 6 algebra intro with single-step equations."""

    skill_id = "yr6_algebra_001"
    question_type = "numeric"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        mode = random.choice(["x_plus", "x_minus", "mul_x", "x_div"])

        if mode == "x_plus":
            x = random.randint(2, 20 + difficulty * 5)
            c = random.randint(2, 15)
            total = x + c
            question = f"Solve x + {c} = {total}. What is x?"
            answer = x
            explanation = f"x = {total} - {c} = {x}."
        elif mode == "x_minus":
            x = random.randint(10, 40 + difficulty * 10)
            c = random.randint(2, 12)
            total = x - c
            question = f"Solve x - {c} = {total}. What is x?"
            answer = x
            explanation = f"x = {total} + {c} = {x}."
        elif mode == "mul_x":
            x = random.randint(2, 12)
            c = random.randint(2, 9)
            total = c * x
            question = f"Solve {c}x = {total}. What is x?"
            answer = x
            explanation = f"x = {total} ÷ {c} = {x}."
        else:
            x = random.randint(2, 12)
            c = random.randint(2, 9)
            total = x
            rhs = x // 1
            question = f"Solve x/{c} = {rhs/c:g}. What is x?"
            answer = x
            explanation = f"Multiply both sides by {c}: x = {x}."

        parameters = {"operation": "identity", "x": x, "mode": mode}
        item_id = deterministic_item_id(
            skill_id=AlgebraIntroTemplate.skill_id,
            difficulty=difficulty,
            parameters=parameters,
            question_text=question,
        )
        return {
            "item_id": item_id,
            "skill_id": AlgebraIntroTemplate.skill_id,
            "question_text": question,
            "question_type": AlgebraIntroTemplate.question_type,
            "difficulty": difficulty,
            "parameters": parameters,
            "correct_answer": str(answer),
            "hint": "Undo the operation to isolate x.",
            "explanation": explanation,
            "validation_rule": "numeric",
        }


TEMPLATES = [
    PlaceValueTemplate,
    AdditionSubtractionTemplate,
    AlgebraIntroTemplate,
]
