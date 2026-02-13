"""
NSW Curriculum-aligned skill tree for Year 3-6
Focus: Number & Algebra, Fractions
"""

def get_skill_tree():
    """Return complete skill tree for Year 3-6"""
    return YEAR_3_SKILLS + YEAR_4_SKILLS + YEAR_5_SKILLS + YEAR_6_SKILLS


# Year 3 Skills - Fractions Introduction
YEAR_3_SKILLS = [
    {
        "skill_id": "yr3_frac_intro_001",
        "description": "Understand fractions as equal parts of a whole",
        "year_level": 3,
        "domain": "Fractions",
        "prerequisites": [],
        "difficulty_levels": [1, 2, 3],
        "common_misconceptions": [
            "Larger denominator means larger fraction",
            "Fractions must always be less than 1"
        ]
    },
    {
        "skill_id": "yr3_frac_compare_001",
        "description": "Compare fractions with same denominator",
        "year_level": 3,
        "domain": "Fractions",
        "prerequisites": ["yr3_frac_intro_001"],
        "difficulty_levels": [1, 2, 3],
        "common_misconceptions": [
            "Comparing numerators when denominators are different"
        ]
    },
    {
        "skill_id": "yr3_frac_identify_001",
        "description": "Identify fractions represented visually",
        "year_level": 3,
        "domain": "Fractions",
        "prerequisites": ["yr3_frac_intro_001"],
        "difficulty_levels": [1, 2, 3],
        "common_misconceptions": [
            "Counting total parts instead of shaded parts"
        ]
    },
    {
        "skill_id": "yr3_num_place_001",
        "description": "Understand place value to hundreds",
        "year_level": 3,
        "domain": "Number & Algebra",
        "prerequisites": [],
        "difficulty_levels": [1, 2, 3],
        "common_misconceptions": [
            "Confusing tens and ones place"
        ]
    },
    {
        "skill_id": "yr3_add_sub_001",
        "description": "Add and subtract within 1000",
        "year_level": 3,
        "domain": "Number & Algebra",
        "prerequisites": ["yr3_num_place_001"],
        "difficulty_levels": [1, 2, 3, 4],
        "common_misconceptions": [
            "Not regrouping when necessary"
        ]
    },
]

# Year 4 Skills - Equivalent Fractions
YEAR_4_SKILLS = [
    {
        "skill_id": "yr4_frac_equiv_001",
        "description": "Understand equivalent fractions",
        "year_level": 4,
        "domain": "Fractions",
        "prerequisites": ["yr3_frac_compare_001"],
        "difficulty_levels": [1, 2, 3, 4],
        "common_misconceptions": [
            "Adding same number to numerator and denominator creates equivalent fraction"
        ]
    },
    {
        "skill_id": "yr4_frac_compare_002",
        "description": "Compare fractions with different denominators",
        "year_level": 4,
        "domain": "Fractions",
        "prerequisites": ["yr4_frac_equiv_001"],
        "difficulty_levels": [2, 3, 4],
        "common_misconceptions": [
            "Comparing numerators only"
        ]
    },
    {
        "skill_id": "yr4_frac_simplify_001",
        "description": "Simplify fractions to lowest terms",
        "year_level": 4,
        "domain": "Fractions",
        "prerequisites": ["yr4_frac_equiv_001"],
        "difficulty_levels": [2, 3, 4],
        "common_misconceptions": [
            "Dividing by any common factor is sufficient"
        ]
    },
    {
        "skill_id": "yr4_decimal_001",
        "description": "Understand decimals to hundredths",
        "year_level": 4,
        "domain": "Number & Algebra",
        "prerequisites": ["yr3_num_place_001"],
        "difficulty_levels": [1, 2, 3],
        "common_misconceptions": [
            "0.3 is larger than 0.29 because 29 > 3"
        ]
    },
    {
        "skill_id": "yr4_mult_div_001",
        "description": "Multiply and divide within 100",
        "year_level": 4,
        "domain": "Number & Algebra",
        "prerequisites": ["yr3_add_sub_001"],
        "difficulty_levels": [1, 2, 3, 4],
        "common_misconceptions": []
    },
]

# Year 5 Skills - Fraction Operations
YEAR_5_SKILLS = [
    {
        "skill_id": "yr5_frac_add_001",
        "description": "Add fractions with same denominator",
        "year_level": 5,
        "domain": "Fractions",
        "prerequisites": ["yr3_frac_compare_001"],
        "difficulty_levels": [1, 2, 3, 4],
        "common_misconceptions": [
            "Adding both numerators and denominators"
        ]
    },
    {
        "skill_id": "yr5_frac_add_002",
        "description": "Add fractions with different denominators",
        "year_level": 5,
        "domain": "Fractions",
        "prerequisites": ["yr5_frac_add_001", "yr4_frac_equiv_001"],
        "difficulty_levels": [2, 3, 4, 5],
        "common_misconceptions": [
            "Adding numerators and denominators separately"
        ]
    },
    {
        "skill_id": "yr5_frac_sub_001",
        "description": "Subtract fractions with same denominator",
        "year_level": 5,
        "domain": "Fractions",
        "prerequisites": ["yr5_frac_add_001"],
        "difficulty_levels": [1, 2, 3, 4],
        "common_misconceptions": [
            "Subtracting both numerators and denominators"
        ]
    },
    {
        "skill_id": "yr5_frac_sub_002",
        "description": "Subtract fractions with different denominators",
        "year_level": 5,
        "domain": "Fractions",
        "prerequisites": ["yr5_frac_sub_001", "yr4_frac_equiv_001"],
        "difficulty_levels": [2, 3, 4, 5],
        "common_misconceptions": []
    },
    {
        "skill_id": "yr5_percent_001",
        "description": "Understand percentages as fractions of 100",
        "year_level": 5,
        "domain": "Number & Algebra",
        "prerequisites": ["yr4_decimal_001"],
        "difficulty_levels": [1, 2, 3],
        "common_misconceptions": [
            "Percentage always means divide by 100"
        ]
    },
]

# Year 6 Skills - Advanced Fractions
YEAR_6_SKILLS = [
    {
        "skill_id": "yr6_frac_mult_001",
        "description": "Multiply fractions",
        "year_level": 6,
        "domain": "Fractions",
        "prerequisites": ["yr5_frac_add_001", "yr4_mult_div_001"],
        "difficulty_levels": [2, 3, 4, 5],
        "common_misconceptions": [
            "Need common denominator to multiply fractions"
        ]
    },
    {
        "skill_id": "yr6_frac_div_001",
        "description": "Divide fractions",
        "year_level": 6,
        "domain": "Fractions",
        "prerequisites": ["yr6_frac_mult_001"],
        "difficulty_levels": [3, 4, 5],
        "common_misconceptions": [
            "Dividing means multiply denominators"
        ]
    },
    {
        "skill_id": "yr6_frac_mixed_001",
        "description": "Convert between mixed numbers and improper fractions",
        "year_level": 6,
        "domain": "Fractions",
        "prerequisites": ["yr5_frac_add_001"],
        "difficulty_levels": [2, 3, 4],
        "common_misconceptions": [
            "Whole number part is the denominator"
        ]
    },
    {
        "skill_id": "yr6_ratio_001",
        "description": "Understand and use ratios",
        "year_level": 6,
        "domain": "Number & Algebra",
        "prerequisites": ["yr4_frac_equiv_001"],
        "difficulty_levels": [2, 3, 4, 5],
        "common_misconceptions": [
            "Ratios and fractions are unrelated"
        ]
    },
    {
        "skill_id": "yr6_algebra_001",
        "description": "Introduction to algebraic expressions",
        "year_level": 6,
        "domain": "Number & Algebra",
        "prerequisites": ["yr4_mult_div_001"],
        "difficulty_levels": [1, 2, 3],
        "common_misconceptions": [
            "Variables always represent unknown numbers"
        ]
    },
]


def get_skills_by_year(year_level):
    """Get all skills for a specific year level"""
    all_skills = get_skill_tree()
    return [s for s in all_skills if s["year_level"] == year_level]


def get_skills_by_domain(domain):
    """Get all skills for a specific domain"""
    all_skills = get_skill_tree()
    return [s for s in all_skills if s["domain"] == domain]
