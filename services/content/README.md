# MathCoach Content Service

Generates and validates curriculum-aligned math content for the MathCoach platform.

## Features

- **NSW Curriculum Alignment**: Skills mapped to NSW Year 3-6 curriculum
- **Deterministic Generation**: All answers are reproducible and verifiable
- **Multi-difficulty**: Items scale from difficulty 1-5
- **Validation**: Automatic answer verification

## Structure

```
content/
├── curriculum/
│   └── nsw_year3_6.py       # Skill tree definition
├── templates/
│   └── fractions.py         # Item generation templates
├── output/
│   ├── skill_tree_v0.json   # Generated skill tree
│   └── content_pack_v0.json # Generated items
├── generate_items.py        # Item generator
└── validate_items.py        # Item validator
```

## Usage

### Generate Items

```bash
python generate_items.py
```

This will:
- Generate 300+ math items
- Save skill tree to `output/skill_tree_v0.json`
- Save items to `output/content_pack_v0.json`

### Validate Items

```bash
python validate_items.py
```

This will:
- Recompute answers for all items
- Verify correctness
- Report any invalid items

## Skill Coverage

**Year 3 (5 skills)**
- Fraction introduction
- Fraction comparison (same denominator)
- Fraction identification
- Place value to hundreds
- Addition/subtraction within 1000

**Year 4 (5 skills)**
- Equivalent fractions
- Fraction comparison (different denominators)
- Fraction simplification
- Decimals to hundredths
- Multiplication/division within 100

**Year 5 (5 skills)**
- Fraction addition (same/different denominators)
- Fraction subtraction (same/different denominators)
- Percentages

**Year 6 (5 skills)**
- Fraction multiplication
- Fraction division
- Mixed numbers and improper fractions
- Ratios
- Algebraic expressions

## Item Templates

### Fraction Comparison Template
- Compares two fractions
- Difficulty 1-2: Same denominator
- Difficulty 3-5: Different denominators

### Fraction Addition Template
- Adds two fractions
- Difficulty 1-2: Same denominator
- Difficulty 3-5: Different denominators, simplification

### Equivalent Fraction Template
- Find equivalent fractions
- Difficulty 1-3: Multiply to get equivalent
- Difficulty 4: Find missing numerator/denominator
- Difficulty 5: Simplify to lowest terms

## Output Format

Each item includes:
- `item_id`: Unique identifier
- `skill_id`: Associated skill
- `question_text`: The question
- `question_type`: "fraction", "numeric", etc.
- `difficulty`: 1-5
- `parameters`: Values used to generate the item
- `correct_answer`: The answer
- `hint`: Student hint
- `explanation`: Detailed explanation
- `validation_rule`: How to validate answer
