"""
Geometry templates (Year 3-5): 2D shape identification, symmetry,
angle classification, 3D shape properties, complementary/supplementary
angle pairs, and first-quadrant coordinates.
"""
import random
import uuid


# -----------------------------------------------------------------------------
# Year 3
# -----------------------------------------------------------------------------

class Shape2DYear3Template:
    skill_id = "yr3_shape_2d_001"
    question_type = "exact_match"
    items_per_difficulty = 100

    # Each entry: (name, sides, equal_sides, right_angles, parallel_pairs)
    SHAPES = [
        {"name": "triangle", "sides": 3, "equal_sides": "varies", "right_angles": 0, "desc": "3 sides"},
        {"name": "square", "sides": 4, "equal_sides": "all", "right_angles": 4, "desc": "4 equal sides and 4 right angles"},
        {"name": "rectangle", "sides": 4, "equal_sides": "opposite", "right_angles": 4, "desc": "4 sides with 4 right angles, opposite sides equal"},
        {"name": "pentagon", "sides": 5, "equal_sides": "varies", "right_angles": 0, "desc": "5 sides"},
        {"name": "hexagon", "sides": 6, "equal_sides": "varies", "right_angles": 0, "desc": "6 sides"},
        {"name": "circle", "sides": 0, "equal_sides": "n/a", "right_angles": 0, "desc": "no straight sides, perfectly round"},
    ]

    @staticmethod
    def generate(difficulty: int):
        # Higher difficulty: include shapes with more sides + tricker descriptions
        if difficulty == 1:
            pool = [s for s in Shape2DYear3Template.SHAPES if s["name"] in ("triangle", "square", "rectangle", "circle")]
        elif difficulty == 2:
            pool = [s for s in Shape2DYear3Template.SHAPES if s["name"] != "hexagon"]
        else:
            pool = Shape2DYear3Template.SHAPES

        shape = random.choice(pool)
        name = shape["name"]
        desc = shape["desc"]

        question = f"Which 2D shape has {desc}?"
        hint = "Match the description to a shape you know. Count sides and angles."
        explanation = f"A {name} has {desc}."

        item_id = f"{Shape2DYear3Template.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": Shape2DYear3Template.skill_id,
            "question_text": question,
            "question_type": Shape2DYear3Template.question_type,
            "difficulty": difficulty,
            "parameters": {"shape_name": name, "description": desc},
            "correct_answer": name,
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "exact_match",
        }


class SymmetryYear3Template:
    skill_id = "yr3_symmetry_001"
    question_type = "numeric"
    items_per_difficulty = 100

    # Number of lines of symmetry for common shapes
    SHAPES = [
        ("square", 4),
        ("rectangle (non-square)", 2),
        ("equilateral triangle", 3),
        ("isosceles triangle (non-equilateral)", 1),
        ("circle (treat as 4 for a school context: horizontal, vertical, and two diagonals)", 4),
        ("regular hexagon", 6),
        ("regular pentagon", 5),
        ("rhombus (non-square)", 2),
        ("parallelogram (non-rectangle, non-rhombus)", 0),
    ]

    @staticmethod
    def generate(difficulty: int):
        if difficulty == 1:
            pool = [s for s in SymmetryYear3Template.SHAPES if s[0] in ("square", "rectangle (non-square)", "equilateral triangle")]
        elif difficulty == 2:
            pool = [s for s in SymmetryYear3Template.SHAPES if s[1] <= 4]
        else:
            pool = SymmetryYear3Template.SHAPES

        shape_name, lines = random.choice(pool)
        # Strip the parenthetical asides for the question text to keep it clean,
        # but include the canonical shape name.
        display_name = shape_name.split(" (")[0]
        question = f"How many lines of symmetry does a {display_name} have?"
        hint = "Fold the shape in your mind — each fold that matches exactly is one line of symmetry."
        if lines == 0:
            explanation = f"A {display_name} has no lines of symmetry — no fold makes both halves match."
        else:
            explanation = f"A {display_name} has {lines} line(s) of symmetry."

        item_id = f"{SymmetryYear3Template.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": SymmetryYear3Template.skill_id,
            "question_text": question,
            "question_type": SymmetryYear3Template.question_type,
            "difficulty": difficulty,
            "parameters": {"shape": shape_name, "lines": lines},
            "correct_answer": str(lines),
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "numeric",
        }


# -----------------------------------------------------------------------------
# Year 4
# -----------------------------------------------------------------------------

class AnglesYear4Template:
    skill_id = "yr4_angles_001"
    question_type = "exact_match"
    items_per_difficulty = 100

    @staticmethod
    def classify(deg: int) -> str:
        if deg < 90:
            return "acute"
        if deg == 90:
            return "right"
        if deg < 180:
            return "obtuse"
        if deg == 180:
            return "straight"
        return "reflex"

    @staticmethod
    def generate(difficulty: int):
        # Difficulty 1: limit to acute/right/obtuse.
        # Difficulty 2: add straight (180).
        # Difficulty 3-4: include reflex (>180).
        if difficulty == 1:
            deg = random.choice(
                [random.randint(10, 89)]  # acute
                + [90]                     # right
                + [random.randint(91, 179)]  # obtuse
            )
        elif difficulty == 2:
            deg = random.choice(
                [random.randint(10, 89), 90, random.randint(91, 179), 180]
            )
        else:
            deg = random.choice(
                [
                    random.randint(5, 89),
                    90,
                    random.randint(91, 179),
                    180,
                    random.randint(181, 350),
                ]
            )

        answer = AnglesYear4Template.classify(deg)
        question = f"An angle measures {deg} degrees. Classify it as acute, right, obtuse, straight, or reflex."
        hint = "acute<90, right=90, obtuse between 90 and 180, straight=180, reflex>180."
        explanation = f"{deg} degrees is {answer} ({AnglesYear4Template._rule(answer)})."

        item_id = f"{AnglesYear4Template.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": AnglesYear4Template.skill_id,
            "question_text": question,
            "question_type": AnglesYear4Template.question_type,
            "difficulty": difficulty,
            "parameters": {"degrees": deg},
            "correct_answer": answer,
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "exact_match",
        }

    @staticmethod
    def _rule(name: str) -> str:
        return {
            "acute": "less than 90 degrees",
            "right": "exactly 90 degrees",
            "obtuse": "between 90 and 180 degrees",
            "straight": "exactly 180 degrees",
            "reflex": "greater than 180 degrees",
        }[name]


class Shape3DYear4Template:
    skill_id = "yr4_shape_3d_001"
    question_type = "numeric"
    items_per_difficulty = 100

    # (name, faces, edges, vertices)
    SHAPES = [
        ("cube", 6, 12, 8),
        ("rectangular prism", 6, 12, 8),
        ("triangular prism", 5, 9, 6),
        ("square pyramid", 5, 8, 5),
        ("triangular pyramid (tetrahedron)", 4, 6, 4),
        ("cone", 2, 1, 1),
        ("cylinder", 3, 2, 0),
        ("sphere", 1, 0, 0),
    ]

    PROPERTIES = ["faces", "edges", "vertices"]

    @staticmethod
    def generate(difficulty: int):
        if difficulty == 1:
            pool = [s for s in Shape3DYear4Template.SHAPES if s[0] in ("cube", "rectangular prism", "sphere")]
        elif difficulty == 2:
            pool = [s for s in Shape3DYear4Template.SHAPES if s[0] in ("cube", "rectangular prism", "square pyramid", "cone", "cylinder", "sphere")]
        else:
            pool = Shape3DYear4Template.SHAPES

        name, faces, edges, vertices = random.choice(pool)
        prop = random.choice(Shape3DYear4Template.PROPERTIES)
        value = {"faces": faces, "edges": edges, "vertices": vertices}[prop]

        question = f"How many {prop} does a {name} have?"
        hint = "Face = flat (or curved) surface. Edge = where two faces meet. Vertex = corner point."
        explanation = f"A {name} has {value} {prop}."

        item_id = f"{Shape3DYear4Template.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": Shape3DYear4Template.skill_id,
            "question_text": question,
            "question_type": Shape3DYear4Template.question_type,
            "difficulty": difficulty,
            "parameters": {"shape": name, "property": prop, "value": value},
            "correct_answer": str(value),
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "numeric",
        }


# -----------------------------------------------------------------------------
# Year 5
# -----------------------------------------------------------------------------

class AnglesYear5Template:
    skill_id = "yr5_angles_001"
    question_type = "numeric"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        # Pick complementary (sum 90) or supplementary (sum 180).
        if difficulty <= 2:
            pair_type = random.choice(["complementary", "supplementary"])
            if pair_type == "complementary":
                given = random.randint(10, 80)
                total = 90
            else:
                given = random.randint(20, 160)
                total = 180
        else:
            pair_type = random.choice(["complementary", "supplementary"])
            if pair_type == "complementary":
                given = random.randint(5, 85)
                total = 90
            else:
                given = random.randint(10, 170)
                total = 180

        missing = total - given
        if pair_type == "complementary":
            question = (
                f"Two angles are complementary. One measures {given} degrees. "
                f"What is the size of the other angle in degrees?"
            )
            hint = "Complementary angles add to 90 degrees."
        else:
            question = (
                f"Two angles are supplementary. One measures {given} degrees. "
                f"What is the size of the other angle in degrees?"
            )
            hint = "Supplementary angles add to 180 degrees."

        explanation = f"{total} - {given} = {missing} degrees."

        item_id = f"{AnglesYear5Template.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": AnglesYear5Template.skill_id,
            "question_text": question,
            "question_type": AnglesYear5Template.question_type,
            "difficulty": difficulty,
            "parameters": {"pair_type": pair_type, "given": given, "total": total},
            "correct_answer": str(missing),
            "hint": hint,
            "explanation": explanation,
            "validation_rule": "numeric",
        }


class CoordinatesYear5Template:
    skill_id = "yr5_coords_001"
    question_type = "exact_match"
    items_per_difficulty = 100

    @staticmethod
    def generate(difficulty: int):
        if difficulty == 1:
            max_xy = 5
        elif difficulty == 2:
            max_xy = 7
        elif difficulty == 3:
            max_xy = 10
        else:
            max_xy = 12

        x = random.randint(0, max_xy)
        y = random.randint(0, max_xy)

        # Mode A: given coords, ask format (returned in "(x, y)" form).
        # Mode B: given (x, y), ask "what is the x-coordinate?" -> numeric answer.
        # We'll alternate; both flow through exact_match by formatting carefully.
        mode = random.choice(["name_point", "read_x", "read_y"])

        if mode == "name_point":
            label = random.choice(["A", "B", "C", "D", "P", "Q"])
            answer = f"({x}, {y})"
            question = (
                f"Point {label} is {x} units right of the origin and {y} units up. "
                f"Write its coordinates in the form (x, y)."
            )
            hint = "Coordinates are written (x, y): horizontal first, then vertical."
            explanation = f"Point {label} = ({x}, {y})."
            params = {"mode": mode, "x": x, "y": y, "label": label}
            validation = "exact_match"
        elif mode == "read_x":
            answer = str(x)
            question = f"A point is at ({x}, {y}). What is its x-coordinate?"
            hint = "The x-coordinate is the first number in (x, y)."
            explanation = f"In ({x}, {y}), the x-coordinate is {x}."
            params = {"mode": mode, "x": x, "y": y}
            validation = "numeric"
        else:
            answer = str(y)
            question = f"A point is at ({x}, {y}). What is its y-coordinate?"
            hint = "The y-coordinate is the second number in (x, y)."
            explanation = f"In ({x}, {y}), the y-coordinate is {y}."
            params = {"mode": mode, "x": x, "y": y}
            validation = "numeric"

        item_id = f"{CoordinatesYear5Template.skill_id}_d{difficulty}_{uuid.uuid4().hex[:8]}"
        return {
            "item_id": item_id,
            "skill_id": CoordinatesYear5Template.skill_id,
            "question_text": question,
            "question_type": validation,
            "difficulty": difficulty,
            "parameters": params,
            "correct_answer": answer,
            "hint": hint,
            "explanation": explanation,
            "validation_rule": validation,
        }


TEMPLATES = [
    Shape2DYear3Template,
    SymmetryYear3Template,
    AnglesYear4Template,
    Shape3DYear4Template,
    AnglesYear5Template,
    CoordinatesYear5Template,
]
