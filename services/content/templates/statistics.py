"""
Statistics & probability templates (Year 3-5): reading data, interpreting
tables, qualitative chance words, mean of a list, and simple probabilities
as fractions.
"""
import random

from .base import deterministic_item_id


# -----------------------------------------------------------------------------
# Year 3
# -----------------------------------------------------------------------------

class DataReadYear3Template:
    skill_id = "yr3_data_read_001"
    question_type = "numeric"
    items_per_difficulty = 100

    CATEGORY_POOLS = [
        ("fruit", ["apples", "oranges", "bananas", "pears", "grapes"]),
        ("pet", ["dogs", "cats", "rabbits", "fish", "birds"]),
        ("colour", ["red", "blue", "green", "yellow", "purple"]),
        ("sport", ["soccer", "netball", "cricket", "swimming", "tennis"]),
    ]

    @staticmethod
    def generate(difficulty: int):
        topic, items = random.choice(DataReadYear3Template.CATEGORY_POOLS)
        if difficulty == 1:
            n_cats = 3
            max_count = 10
        elif difficulty == 2:
            n_cats = 4
            max_count = 15
        else:
            n_cats = 5
            max_count = 20

        chosen = random.sample(items, n_cats)
        counts = {name: random.randint(1, max_count) for name in chosen}
        target = random.choice(chosen)

        table_str = ", ".join(f"{k}: {v}" for k, v in counts.items())
        question = (
            f"Sarah counted {topic}s in the classroom and got these results: "
            f"{table_str}. How many {target} are there?"
        )
        hint = "Find the row (or bar) for the category, then read its value."
        explanation = f"From the data, {target} = {counts[target]}."

        parameters = {"topic": topic, "counts": counts, "target": target}
        item_id = deterministic_item_id(
            skill_id=DataReadYear3Template.skill_id,
            difficulty=difficulty,
            parameters=parameters,
            question_text=question,
        )
        return {
            "item_id": item_id,
            "skill_id": DataReadYear3Template.skill_id,
            "question_text": question,
            "question_type": DataReadYear3Template.question_type,
            "difficulty": difficulty,
            "parameters": parameters,
            "correct_answer": str(counts[target]),
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "numeric",
        }


# -----------------------------------------------------------------------------
# Year 4
# -----------------------------------------------------------------------------

class DataInterpretYear4Template:
    skill_id = "yr4_data_interpret_001"
    question_type = "numeric"
    items_per_difficulty = 100

    CATEGORY_POOLS = DataReadYear3Template.CATEGORY_POOLS

    @staticmethod
    def generate(difficulty: int):
        topic, items = random.choice(DataInterpretYear4Template.CATEGORY_POOLS)
        if difficulty == 1:
            n_cats = 3
            max_count = 10
        elif difficulty == 2:
            n_cats = 4
            max_count = 15
        elif difficulty == 3:
            n_cats = 5
            max_count = 20
        else:
            n_cats = 5
            max_count = 30

        chosen = random.sample(items, n_cats)
        # Ensure unique values so "most" and "least" are well-defined.
        values = random.sample(range(1, max_count + 1), n_cats)
        counts = dict(zip(chosen, values))

        # Pick a question type: total, most, least
        q_type = random.choice(["total", "most", "least"])
        table_str = ", ".join(f"{k}: {v}" for k, v in counts.items())

        if q_type == "total":
            answer = sum(counts.values())
            question = (
                f"A survey of favourite {topic}s gave these results: "
                f"{table_str}. What is the total number of votes?"
            )
            hint = "Add every value in the table together."
            explanation = (
                f"{' + '.join(str(v) for v in counts.values())} = {answer}."
            )
            validation = "numeric"
            correct = str(answer)
        elif q_type == "most":
            best = max(counts, key=counts.get)
            answer = counts[best]
            question = (
                f"A survey of favourite {topic}s gave these results: "
                f"{table_str}. How many votes did the most popular option get?"
            )
            hint = "Find the largest value in the table."
            explanation = f"The most popular is {best} with {answer} votes."
            validation = "numeric"
            correct = str(answer)
        else:  # least
            worst = min(counts, key=counts.get)
            answer = counts[worst]
            question = (
                f"A survey of favourite {topic}s gave these results: "
                f"{table_str}. How many votes did the least popular option get?"
            )
            hint = "Find the smallest value in the table."
            explanation = f"The least popular is {worst} with {answer} votes."
            validation = "numeric"
            correct = str(answer)

        parameters = {"topic": topic, "counts": counts, "operation": q_type}
        item_id = deterministic_item_id(
            skill_id=DataInterpretYear4Template.skill_id,
            difficulty=difficulty,
            parameters=parameters,
            question_text=question,
        )
        return {
            "item_id": item_id,
            "skill_id": DataInterpretYear4Template.skill_id,
            "question_text": question,
            "question_type": validation,
            "difficulty": difficulty,
            "parameters": parameters,
            "correct_answer": correct,
            "hint": hint,
            "explanation": explanation,
            "validation_rule": validation,
        }


class ChanceYear4Template:
    skill_id = "yr4_chance_001"
    question_type = "exact_match"
    items_per_difficulty = 100

    # (event_text, classification)
    EVENTS = [
        ("the sun will rise tomorrow morning", "certain"),
        ("a fair coin lands on heads", "likely"),  # often glossed as 'even chance' but 'likely' is acceptable
        ("you roll a 7 on a standard six-sided die", "impossible"),
        ("it will snow in Sydney in summer", "impossible"),
        ("a baby will be born today somewhere in the world", "certain"),
        ("you will see a kangaroo in your classroom today", "unlikely"),
        ("the next car driving past is red", "unlikely"),
        ("you will eat food this week", "certain"),
        ("a randomly chosen day of the week is a weekday", "likely"),
        ("a randomly chosen day of the week is Saturday", "unlikely"),
        ("a fish learns to ride a bicycle", "impossible"),
        ("the school bell rings before the end of the day", "certain"),
        ("you flip a coin and it lands on its edge", "unlikely"),
        ("a randomly chosen letter from the alphabet is a vowel", "unlikely"),
    ]

    # For determinism in answers we use a small fixed lexicon.
    CLASSES = ["impossible", "unlikely", "likely", "certain"]

    @staticmethod
    def generate(difficulty: int):
        # Difficulty narrows or widens the pool slightly.
        if difficulty == 1:
            pool = [e for e in ChanceYear4Template.EVENTS if e[1] in ("impossible", "certain")]
        elif difficulty == 2:
            pool = [e for e in ChanceYear4Template.EVENTS if e[1] in ("impossible", "certain", "likely")]
        else:
            pool = ChanceYear4Template.EVENTS

        event_text, classification = random.choice(pool)
        question = (
            f"Classify the chance of this event: '{event_text}'. "
            f"Choose one of: impossible, unlikely, likely, certain."
        )
        hint = "Impossible can never happen; unlikely is rare; likely happens often; certain always happens."
        explanation = f"This event is {classification}."

        parameters = {"event": event_text, "options": ChanceYear4Template.CLASSES}
        item_id = deterministic_item_id(
            skill_id=ChanceYear4Template.skill_id,
            difficulty=difficulty,
            parameters=parameters,
            question_text=question,
        )
        return {
            "item_id": item_id,
            "skill_id": ChanceYear4Template.skill_id,
            "question_text": question,
            "question_type": ChanceYear4Template.question_type,
            "difficulty": difficulty,
            "parameters": parameters,
            "correct_answer": classification,
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "exact_match",
        }


# -----------------------------------------------------------------------------
# Year 5
# -----------------------------------------------------------------------------

class DataAvgYear5Template:
    skill_id = "yr5_data_avg_001"
    question_type = "numeric"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        # Generate a list whose sum is divisible by its length so mean is whole.
        if difficulty <= 2:
            n = random.choice([4, 5])
            max_v = 10
        elif difficulty == 3:
            n = random.choice([5, 6])
            max_v = 15
        else:
            n = random.choice([5, 6])
            max_v = 20

        # Choose a target mean, then build a list around it.
        target = random.randint(3, max_v)
        # Construct: start with all = target, then redistribute to add variance.
        values = [target] * n
        # Apply pairwise swaps: pick two indices i,j and shift +k/-k.
        # Always preserves total => mean stays integer.
        shifts = random.randint(1, n)
        for _ in range(shifts):
            i, j = random.sample(range(n), 2)
            # Max k we can move from i to j without violating bounds:
            #   values[i] - k >= 1   =>  k <= values[i] - 1
            #   values[j] + k <= max_v =>  k <= max_v - values[j]
            k_max = min(values[i] - 1, max_v - values[j])
            if k_max < 1:
                continue
            k = random.randint(1, k_max)
            values[i] -= k
            values[j] += k

        total = sum(values)
        mean = total // n
        # Sanity: should be exact because we only swapped equal amounts.
        if total % n != 0:
            # Fallback: rebuild as flat list at target
            values = [target] * n
            total = target * n
            mean = target

        random.shuffle(values)
        list_str = ", ".join(str(v) for v in values)
        question = f"Find the mean of these numbers: {list_str}."
        hint = "Mean = sum of values divided by how many values there are."
        explanation = (
            f"Sum = {' + '.join(str(v) for v in values)} = {total}. "
            f"Count = {n}. Mean = {total} / {n} = {mean}."
        )

        parameters = {"values": values, "count": n, "sum": total}
        item_id = deterministic_item_id(
            skill_id=DataAvgYear5Template.skill_id,
            difficulty=difficulty,
            parameters=parameters,
            question_text=question,
        )
        return {
            "item_id": item_id,
            "skill_id": DataAvgYear5Template.skill_id,
            "question_text": question,
            "question_type": DataAvgYear5Template.question_type,
            "difficulty": difficulty,
            "parameters": parameters,
            "correct_answer": str(mean),
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "numeric",
        }


class ChanceYear5Template:
    skill_id = "yr5_chance_001"
    question_type = "fraction"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        # We support: coin flip, dice roll, marbles in a bag, spinner
        scenario = random.choice(["dice", "coin", "marbles", "spinner"])

        if scenario == "dice":
            # Standard 6-sided die. Question variants:
            # - P(specific number) = 1/6
            # - P(even) = 3/6, P(odd) = 3/6
            # - P(greater than k) for k in 1..5
            variant = random.choice(["single", "even", "odd", "greater"])
            if variant == "single":
                target = random.randint(1, 6)
                num, denom = 1, 6
                event = f"rolling a {target}"
            elif variant == "even":
                num, denom = 3, 6
                event = "rolling an even number"
            elif variant == "odd":
                num, denom = 3, 6
                event = "rolling an odd number"
            else:
                k = random.randint(1, 5)
                num = 6 - k  # numbers > k: k+1..6
                denom = 6
                event = f"rolling a number greater than {k}"

            question = f"A fair six-sided die is rolled. What is the probability of {event}? Give your answer as a fraction in the form a/b."
            hint = "P(event) = favourable outcomes / total outcomes. A die has 6 sides."
            explanation = f"Favourable = {num}, total = {denom}. P({event}) = {num}/{denom}."

        elif scenario == "coin":
            side = random.choice(["heads", "tails"])
            num, denom = 1, 2
            event = f"a fair coin landing on {side}"
            question = f"A fair coin is flipped. What is the probability of {event}? Give your answer as a fraction in the form a/b."
            hint = "A coin has 2 sides, each equally likely."
            explanation = f"Favourable = 1 ({side}), total = 2 (heads, tails). P = 1/2."

        elif scenario == "marbles":
            # Bag of red and blue marbles.
            red = random.randint(1, 6)
            blue = random.randint(1, 6)
            total = red + blue
            colour = random.choice(["red", "blue"])
            num = red if colour == "red" else blue
            denom = total
            event = f"drawing a {colour} marble"
            question = (
                f"A bag contains {red} red and {blue} blue marbles. "
                f"One marble is drawn at random. What is the probability of {event}? "
                f"Give your answer as a fraction in the form a/b."
            )
            hint = "P = favourable / total. Total = all marbles in the bag."
            explanation = f"Favourable = {num} ({colour}), total = {denom}. P = {num}/{denom}."

        else:  # spinner
            sections = random.choice([4, 5, 6, 8])
            favourable = random.randint(1, sections - 1)
            num, denom = favourable, sections
            event = f"landing on a favourable section"
            question = (
                f"A spinner is divided into {sections} equal sections. "
                f"{favourable} of them are coloured red. What is the probability "
                f"of the spinner landing on red? Give your answer as a fraction in the form a/b."
            )
            hint = "P = favourable sections / total equal sections."
            explanation = f"Favourable = {favourable}, total = {sections}. P = {favourable}/{sections}."

        answer = f"{num}/{denom}"
        parameters = {"scenario": scenario, "num": num, "denom": denom}
        item_id = deterministic_item_id(
            skill_id=ChanceYear5Template.skill_id,
            difficulty=difficulty,
            parameters=parameters,
            question_text=question,
        )
        return {
            "item_id": item_id,
            "skill_id": ChanceYear5Template.skill_id,
            "question_text": question,
            "question_type": ChanceYear5Template.question_type,
            "difficulty": difficulty,
            "parameters": parameters,
            "correct_answer": answer,
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "fraction",
        }


TEMPLATES = [
    DataReadYear3Template,
    DataInterpretYear4Template,
    ChanceYear4Template,
    DataAvgYear5Template,
    ChanceYear5Template,
]
