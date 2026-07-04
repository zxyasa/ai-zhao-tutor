"""
Measurement templates (Year 3-5): length, time, money, area, perimeter,
volume, and unit conversion. All math deterministic and verifiable.
"""
import random

from .base import deterministic_item_id


# -----------------------------------------------------------------------------
# Year 3
# -----------------------------------------------------------------------------

class LengthYear3Template:
    skill_id = "yr3_length_001"
    question_type = "numeric"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        # d1: cm directly; d2: m to cm; d3: cm to m (whole metres)
        if difficulty == 1:
            cm = random.randint(5, 50)
            question = f"A pencil is {cm} cm long. How many centimetres is that?"
            answer = cm
            unit = "cm"
            hint = "Read the value, units stay the same."
            explanation = f"The pencil is {cm} cm long."
            params = {"operation": "identity", "value": cm, "unit": "cm"}
        elif difficulty == 2:
            metres = random.randint(1, 9)
            cm = metres * 100
            question = f"A rope is {metres} m long. How many centimetres is that?"
            answer = cm
            unit = "cm"
            hint = "1 m = 100 cm."
            explanation = f"{metres} m x 100 = {cm} cm."
            params = {"operation": "m_to_cm", "value": metres}
        else:
            metres = random.randint(2, 9)
            cm = metres * 100
            question = f"A garden hose is {cm} cm long. How many metres is that?"
            answer = metres
            unit = "m"
            hint = "Divide by 100 because 100 cm = 1 m."
            explanation = f"{cm} cm / 100 = {metres} m."
            params = {"operation": "cm_to_m", "value": cm}

        parameters = {**params, "answer_unit": unit}
        item_id = deterministic_item_id(
            skill_id=LengthYear3Template.skill_id,
            difficulty=difficulty,
            parameters=parameters,
            question_text=question,
        )
        return {
            "item_id": item_id,
            "skill_id": LengthYear3Template.skill_id,
            "question_text": question,
            "question_type": LengthYear3Template.question_type,
            "difficulty": difficulty,
            "parameters": parameters,
            "correct_answer": str(answer),
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "numeric",
        }


class TimeYear3Template:
    skill_id = "yr3_time_001"
    question_type = "numeric"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        # We always ask "how many minutes past the hour?" so answer is numeric.
        hour = random.randint(1, 12)
        if difficulty == 1:
            minutes = random.choice([0, 15, 30, 45])
        elif difficulty == 2:
            minutes = random.choice([5, 10, 20, 25, 35, 40, 50, 55])
        else:
            minutes = random.choice([5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])

        time_str = f"{hour}:{minutes:02d}"
        question = (
            f"A digital clock shows {time_str}. "
            f"How many minutes past {hour} o'clock is it?"
        )
        hint = "Read the digits after the colon — those are the minutes past the hour."
        explanation = f"{time_str} means {minutes} minutes past {hour} o'clock."

        parameters = {"hour": hour, "minutes": minutes, "display": time_str}
        item_id = deterministic_item_id(
            skill_id=TimeYear3Template.skill_id,
            difficulty=difficulty,
            parameters=parameters,
            question_text=question,
        )
        return {
            "item_id": item_id,
            "skill_id": TimeYear3Template.skill_id,
            "question_text": question,
            "question_type": TimeYear3Template.question_type,
            "difficulty": difficulty,
            "parameters": parameters,
            "correct_answer": str(minutes),
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "numeric",
        }


class MoneyYear3Template:
    skill_id = "yr3_money_001"
    question_type = "numeric"
    items_per_difficulty = 100

    # Australian coin denominations in cents
    COINS = [5, 10, 20, 50, 100, 200]  # 5c, 10c, 20c, 50c, $1, $2

    @staticmethod
    def generate(difficulty: int):
        # We pick coins, sum, and ensure the total <= $5 (500c).
        if difficulty == 1:
            n_coins = random.randint(2, 3)
        elif difficulty == 2:
            n_coins = random.randint(3, 5)
        else:
            n_coins = random.randint(4, 6)

        # Sample coins until total <= 500c; cap retries.
        for _ in range(20):
            coins = [random.choice(MoneyYear3Template.COINS) for _ in range(n_coins)]
            total = sum(coins)
            if total <= 500:
                break
        else:
            # Fallback: use only small coins
            coins = [random.choice([5, 10, 20]) for _ in range(n_coins)]
            total = sum(coins)

        def label(c):
            return f"${c // 100}" if c >= 100 and c % 100 == 0 else f"{c}c"

        coin_list = ", ".join(label(c) for c in coins)
        question = f"Sarah has these coins: {coin_list}. What is the total in cents?"
        hint = "Add each coin's value in cents. $1 = 100c, $2 = 200c."
        explanation = f"{' + '.join(str(c) for c in coins)} = {total} cents."

        parameters = {"coins_cents": coins, "answer_unit": "cents"}
        item_id = deterministic_item_id(
            skill_id=MoneyYear3Template.skill_id,
            difficulty=difficulty,
            parameters=parameters,
            question_text=question,
        )
        return {
            "item_id": item_id,
            "skill_id": MoneyYear3Template.skill_id,
            "question_text": question,
            "question_type": MoneyYear3Template.question_type,
            "difficulty": difficulty,
            "parameters": parameters,
            "correct_answer": str(total),
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "numeric",
        }


# -----------------------------------------------------------------------------
# Year 4
# -----------------------------------------------------------------------------

class AreaYear4Template:
    skill_id = "yr4_area_001"
    question_type = "numeric"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        if difficulty == 1:
            l, w = random.randint(2, 5), random.randint(2, 5)
        elif difficulty == 2:
            l, w = random.randint(3, 8), random.randint(2, 6)
        elif difficulty == 3:
            l, w = random.randint(4, 10), random.randint(3, 10)
        else:
            l, w = random.randint(5, 12), random.randint(4, 12)

        area = l * w
        question = (
            f"A rectangle is {l} cm long and {w} cm wide. "
            f"What is its area in square centimetres?"
        )
        hint = "Area of a rectangle = length x width."
        explanation = f"{l} x {w} = {area} square cm."

        parameters = {"length": l, "width": w, "answer_unit": "sq cm"}
        item_id = deterministic_item_id(
            skill_id=AreaYear4Template.skill_id,
            difficulty=difficulty,
            parameters=parameters,
            question_text=question,
        )
        return {
            "item_id": item_id,
            "skill_id": AreaYear4Template.skill_id,
            "question_text": question,
            "question_type": AreaYear4Template.question_type,
            "difficulty": difficulty,
            "parameters": parameters,
            "correct_answer": str(area),
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "numeric",
        }


class PerimeterYear4Template:
    skill_id = "yr4_perimeter_001"
    question_type = "numeric"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        if difficulty == 1:
            l, w = random.randint(2, 5), random.randint(2, 5)
        elif difficulty == 2:
            l, w = random.randint(3, 8), random.randint(2, 6)
        elif difficulty == 3:
            l, w = random.randint(4, 10), random.randint(3, 10)
        else:
            l, w = random.randint(5, 15), random.randint(4, 12)

        perimeter = 2 * (l + w)
        question = (
            f"A rectangle is {l} cm long and {w} cm wide. "
            f"What is its perimeter in centimetres?"
        )
        hint = "Perimeter = 2 x (length + width)."
        explanation = f"2 x ({l} + {w}) = 2 x {l + w} = {perimeter} cm."

        parameters = {"length": l, "width": w, "answer_unit": "cm"}
        item_id = deterministic_item_id(
            skill_id=PerimeterYear4Template.skill_id,
            difficulty=difficulty,
            parameters=parameters,
            question_text=question,
        )
        return {
            "item_id": item_id,
            "skill_id": PerimeterYear4Template.skill_id,
            "question_text": question,
            "question_type": PerimeterYear4Template.question_type,
            "difficulty": difficulty,
            "parameters": parameters,
            "correct_answer": str(perimeter),
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "numeric",
        }


class VolumeYear4Template:
    skill_id = "yr4_volume_001"
    question_type = "numeric"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        if difficulty == 1:
            l, w, h = random.randint(2, 3), random.randint(2, 3), random.randint(2, 3)
        elif difficulty == 2:
            l, w, h = random.randint(2, 4), random.randint(2, 4), random.randint(2, 4)
        elif difficulty == 3:
            l, w, h = random.randint(2, 5), random.randint(2, 5), random.randint(2, 5)
        else:
            l, w, h = random.randint(3, 6), random.randint(2, 6), random.randint(2, 6)

        volume = l * w * h
        question = (
            f"A box is made of unit cubes. It is {l} cubes long, "
            f"{w} cubes wide, and {h} cubes tall. "
            f"How many unit cubes does it contain?"
        )
        hint = "Volume = length x width x height."
        explanation = f"{l} x {w} x {h} = {volume} cubic units."

        parameters = {"length": l, "width": w, "height": h, "answer_unit": "cubic units"}
        item_id = deterministic_item_id(
            skill_id=VolumeYear4Template.skill_id,
            difficulty=difficulty,
            parameters=parameters,
            question_text=question,
        )
        return {
            "item_id": item_id,
            "skill_id": VolumeYear4Template.skill_id,
            "question_text": question,
            "question_type": VolumeYear4Template.question_type,
            "difficulty": difficulty,
            "parameters": parameters,
            "correct_answer": str(volume),
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "numeric",
        }


# -----------------------------------------------------------------------------
# Year 5
# -----------------------------------------------------------------------------

class AreaYear5Template:
    skill_id = "yr5_area_001"
    question_type = "numeric"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        # Mix rectangles and triangles; for triangles ensure b*h is even
        # so area is whole.
        shape = random.choice(["rectangle", "triangle"])

        if difficulty <= 2:
            a = random.randint(3, 8)
            b = random.randint(2, 8)
        elif difficulty == 3:
            a = random.randint(4, 12)
            b = random.randint(3, 10)
        else:
            a = random.randint(5, 15)
            b = random.randint(4, 12)

        if shape == "triangle":
            # Make sure base*height is even so 1/2 * b * h is an integer.
            if (a * b) % 2 != 0:
                b += 1
            area = (a * b) // 2
            question = (
                f"A triangle has a base of {a} cm and a perpendicular height of "
                f"{b} cm. What is its area in square centimetres?"
            )
            hint = "Area of a triangle = 1/2 x base x height."
            explanation = f"1/2 x {a} x {b} = {area} square cm."
            params = {"shape": "triangle", "base": a, "height": b, "answer_unit": "sq cm"}
        else:
            area = a * b
            question = (
                f"A rectangle is {a} cm by {b} cm. "
                f"What is its area in square centimetres?"
            )
            hint = "Area of a rectangle = length x width."
            explanation = f"{a} x {b} = {area} square cm."
            params = {"shape": "rectangle", "length": a, "width": b, "answer_unit": "sq cm"}

        item_id = deterministic_item_id(
            skill_id=AreaYear5Template.skill_id,
            difficulty=difficulty,
            parameters=params,
            question_text=question,
        )
        return {
            "item_id": item_id,
            "skill_id": AreaYear5Template.skill_id,
            "question_text": question,
            "question_type": AreaYear5Template.question_type,
            "difficulty": difficulty,
            "parameters": params,
            "correct_answer": str(area),
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "numeric",
        }


class PerimeterYear5Template:
    skill_id = "yr5_perimeter_001"
    question_type = "numeric"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        # Build an L-shape from a big rectangle (W x H) with a smaller
        # rectangle (w x h) cut from the top-right corner.
        # Perimeter of the resulting L equals 2 * (W + H) because the cut
        # adds two new sides whose lengths sum equals what they replace
        # only when the corner is fully removed. To keep it interesting,
        # we make the cut interior (not full-edge) so the perimeter equals
        # 2*(W + H) when w < W and h < H -> the cut adds 2 new edges of
        # length w and h, but removes nothing from the outer outline; the
        # actual L perimeter is 2*W + 2*H. We verify below.
        if difficulty <= 2:
            W = random.randint(5, 10)
            H = random.randint(4, 8)
        elif difficulty == 3:
            W = random.randint(6, 14)
            H = random.randint(5, 12)
        else:
            W = random.randint(8, 18)
            H = random.randint(6, 14)

        w = random.randint(1, W - 2)
        h = random.randint(1, H - 2)

        # L-shape perimeter when notch is at one corner = 2*(W + H).
        # The notch contributes +w +h on the inside but removes -w -h
        # from the outside, net zero.
        perimeter = 2 * (W + H)

        question = (
            f"An L-shaped garden is formed by taking a {W} m by {H} m rectangle "
            f"and removing a {w} m by {h} m rectangle from one corner. "
            f"What is the perimeter of the L-shape in metres?"
        )
        hint = (
            "Walk around the outside of the L. The notch adds two sides "
            "but removes none from the outer rectangle — so perimeter = "
            "2 x (length + width) of the original rectangle."
        )
        explanation = (
            f"Perimeter = 2 x ({W} + {H}) = 2 x {W + H} = {perimeter} m. "
            f"The {w} m x {h} m notch contributes {w} + {h} on the inside "
            f"and removes {w} + {h} from the outside — they cancel."
        )

        parameters = {
            "outer_length": W,
            "outer_width": H,
            "notch_length": w,
            "notch_width": h,
            "answer_unit": "m",
        }
        item_id = deterministic_item_id(
            skill_id=PerimeterYear5Template.skill_id,
            difficulty=difficulty,
            parameters=parameters,
            question_text=question,
        )
        return {
            "item_id": item_id,
            "skill_id": PerimeterYear5Template.skill_id,
            "question_text": question,
            "question_type": PerimeterYear5Template.question_type,
            "difficulty": difficulty,
            "parameters": parameters,
            "correct_answer": str(perimeter),
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "numeric",
        }


class UnitConvertYear5Template:
    skill_id = "yr5_unit_convert_001"
    question_type = "numeric"
    items_per_difficulty = 100

    # (from_unit, to_unit, factor)  meaning: value_in_from * factor = value_in_to
    CONVERSIONS = [
        ("cm", "mm", 10),
        ("m", "cm", 100),
        ("km", "m", 1000),
        ("L", "mL", 1000),
        ("kg", "g", 1000),
    ]

    @staticmethod
    def generate(difficulty: int):
        from_unit, to_unit, factor = random.choice(UnitConvertYear5Template.CONVERSIONS)

        # Direction: difficulty 1-2 mostly "small->big factor multiply",
        # 3-4 introduce inverse (big_unit value -> small_unit count).
        if difficulty <= 2:
            direction = "multiply"
        elif difficulty == 3:
            direction = random.choice(["multiply", "divide"])
        else:
            direction = "divide"

        if direction == "multiply":
            # value in `from_unit`, answer in `to_unit`
            if difficulty == 1:
                value = random.randint(1, 9)
            elif difficulty == 2:
                value = random.randint(2, 20)
            else:
                value = random.randint(2, 50)
            answer = value * factor
            question = f"Convert {value} {from_unit} to {to_unit}."
            hint = f"1 {from_unit} = {factor} {to_unit}. Multiply by {factor}."
            explanation = f"{value} x {factor} = {answer} {to_unit}."
            params = {
                "value": value,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "factor": factor,
                "direction": "multiply",
                "answer_unit": to_unit,
            }
        else:
            # We want a whole-number answer when going to_unit -> from_unit,
            # so pick a multiple of `factor` as the to_unit value.
            multiplier = random.randint(2, 12)
            to_value = multiplier * factor
            answer = multiplier
            question = f"Convert {to_value} {to_unit} to {from_unit}."
            hint = f"1 {from_unit} = {factor} {to_unit}. Divide by {factor}."
            explanation = f"{to_value} / {factor} = {answer} {from_unit}."
            params = {
                "value": to_value,
                "from_unit": to_unit,
                "to_unit": from_unit,
                "factor": factor,
                "direction": "divide",
                "answer_unit": from_unit,
            }

        item_id = deterministic_item_id(
            skill_id=UnitConvertYear5Template.skill_id,
            difficulty=difficulty,
            parameters=params,
            question_text=question,
        )
        return {
            "item_id": item_id,
            "skill_id": UnitConvertYear5Template.skill_id,
            "question_text": question,
            "question_type": UnitConvertYear5Template.question_type,
            "difficulty": difficulty,
            "parameters": params,
            "correct_answer": str(answer),
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "numeric",
        }


TEMPLATES = [
    LengthYear3Template,
    TimeYear3Template,
    MoneyYear3Template,
    AreaYear4Template,
    PerimeterYear4Template,
    VolumeYear4Template,
    AreaYear5Template,
    PerimeterYear5Template,
    UnitConvertYear5Template,
]
