# MathCoach Shared Schemas

Shared Pydantic models used across the MathCoach platform (API, content service, and client apps).

## Installation

```bash
pip install -e .
```

## Usage

```python
from mathcoach_shared.schemas import Skill, Item, Event, Mastery

# Create a skill
skill = Skill(
    skill_id="yr3_frac_intro_001",
    description="Understand fractions as equal parts of a whole",
    year_level=3,
    domain="Fractions"
)

# Create an item
item = Item(
    item_id="item_001",
    skill_id="yr3_frac_intro_001",
    question_text="What fraction is shaded?",
    question_type="fraction",
    difficulty=1,
    parameters={"numerator": 3, "denominator": 4},
    correct_answer="3/4",
    hint="Count the shaded parts",
    explanation="3 out of 4 parts are shaded",
    validation_rule="exact_match"
)
```

## Models

- **Skill**: Curriculum skill definition
- **Item**: Question/problem instance
- **Event**: Student answer submission
- **Mastery**: Student progress tracking
