"""
NSW Curriculum-aligned skill tree for Year 3-6
Focus: Number & Algebra, Fractions
"""

def get_skill_tree():
    """Return complete skill tree for Year 3-6"""
    return (
        YEAR_3_SKILLS
        + YEAR_4_SKILLS
        + YEAR_5_SKILLS
        + YEAR_6_SKILLS
        + YEAR_3_MEASUREMENT
        + YEAR_4_MEASUREMENT
        + YEAR_5_MEASUREMENT
        + YEAR_3_GEOMETRY
        + YEAR_4_GEOMETRY
        + YEAR_5_GEOMETRY
        + YEAR_3_STATS
        + YEAR_4_STATS
        + YEAR_5_STATS
    )


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


# =============================================================================
# Measurement Skills (Year 3-5)
# =============================================================================

YEAR_3_MEASUREMENT = [
    {
        "skill_id": "yr3_length_001",
        "description": "Measure and compare lengths in cm and m",
        "year_level": 3,
        "domain": "Measurement",
        "prerequisites": [],
        "difficulty_levels": [1, 2, 3],
        "common_misconceptions": [
            "1 m equals 10 cm instead of 100 cm",
            "Starting measurement from 1 on the ruler instead of 0"
        ]
    },
    {
        "skill_id": "yr3_time_001",
        "description": "Tell time to the nearest 5 minutes",
        "year_level": 3,
        "domain": "Measurement",
        "prerequisites": [],
        "difficulty_levels": [1, 2, 3],
        "common_misconceptions": [
            "Confusing the hour and minute hand",
            "Reading 'quarter to' as 'quarter past'"
        ]
    },
    {
        "skill_id": "yr3_money_001",
        "description": "Add coin values to make totals up to $5",
        "year_level": 3,
        "domain": "Measurement",
        "prerequisites": ["yr3_add_sub_001"],
        "difficulty_levels": [1, 2, 3],
        "common_misconceptions": [
            "Treating cents and dollars as the same unit",
            "Ignoring 5c rounding for cash totals"
        ]
    },
]

YEAR_4_MEASUREMENT = [
    {
        "skill_id": "yr4_area_001",
        "description": "Find area of rectangles by counting squares and using L x W",
        "year_level": 4,
        "domain": "Measurement",
        "prerequisites": ["yr4_mult_div_001"],
        "difficulty_levels": [1, 2, 3, 4],
        "common_misconceptions": [
            "Confusing area with perimeter",
            "Adding length and width instead of multiplying"
        ]
    },
    {
        "skill_id": "yr4_perimeter_001",
        "description": "Find perimeter of rectangles by adding side lengths",
        "year_level": 4,
        "domain": "Measurement",
        "prerequisites": ["yr3_add_sub_001"],
        "difficulty_levels": [1, 2, 3, 4],
        "common_misconceptions": [
            "Only adding two sides instead of all four",
            "Confusing perimeter with area"
        ]
    },
    {
        "skill_id": "yr4_volume_001",
        "description": "Find volume of cubes and cuboids by counting unit cubes",
        "year_level": 4,
        "domain": "Measurement",
        "prerequisites": ["yr4_mult_div_001"],
        "difficulty_levels": [1, 2, 3, 4],
        "common_misconceptions": [
            "Only counting visible cubes",
            "Adding dimensions instead of multiplying"
        ]
    },
]

YEAR_5_MEASUREMENT = [
    {
        "skill_id": "yr5_area_001",
        "description": "Calculate area of rectangles and triangles",
        "year_level": 5,
        "domain": "Measurement",
        "prerequisites": ["yr4_area_001"],
        "difficulty_levels": [2, 3, 4, 5],
        "common_misconceptions": [
            "Forgetting the 1/2 factor for triangles",
            "Using slant length instead of perpendicular height"
        ]
    },
    {
        "skill_id": "yr5_perimeter_001",
        "description": "Calculate perimeter of composite L-shapes",
        "year_level": 5,
        "domain": "Measurement",
        "prerequisites": ["yr4_perimeter_001"],
        "difficulty_levels": [2, 3, 4, 5],
        "common_misconceptions": [
            "Missing the inner step sides",
            "Double-counting overlapping edges"
        ]
    },
    {
        "skill_id": "yr5_unit_convert_001",
        "description": "Convert between mm/cm/m/km, mL/L, and g/kg",
        "year_level": 5,
        "domain": "Measurement",
        "prerequisites": ["yr3_length_001"],
        "difficulty_levels": [1, 2, 3, 4],
        "common_misconceptions": [
            "Multiplying when should divide and vice versa",
            "Using wrong conversion factor (e.g. 10 instead of 1000)"
        ]
    },
]


# =============================================================================
# Geometry Skills (Year 3-5)
# =============================================================================

YEAR_3_GEOMETRY = [
    {
        "skill_id": "yr3_shape_2d_001",
        "description": "Identify common 2D shapes by their properties",
        "year_level": 3,
        "domain": "Geometry",
        "prerequisites": [],
        "difficulty_levels": [1, 2, 3],
        "common_misconceptions": [
            "Calling any 4-sided shape a square",
            "Thinking orientation changes the shape's name"
        ]
    },
    {
        "skill_id": "yr3_symmetry_001",
        "description": "Identify lines of symmetry in 2D shapes",
        "year_level": 3,
        "domain": "Geometry",
        "prerequisites": ["yr3_shape_2d_001"],
        "difficulty_levels": [1, 2, 3],
        "common_misconceptions": [
            "Diagonals are always lines of symmetry",
            "All shapes have at least one line of symmetry"
        ]
    },
]

YEAR_4_GEOMETRY = [
    {
        "skill_id": "yr4_angles_001",
        "description": "Classify angles as acute, right, obtuse, straight, or reflex",
        "year_level": 4,
        "domain": "Geometry",
        "prerequisites": [],
        "difficulty_levels": [1, 2, 3, 4],
        "common_misconceptions": [
            "All angles greater than 90 are obtuse, even reflex",
            "Confusing right angle (90) with straight angle (180)"
        ]
    },
    {
        "skill_id": "yr4_shape_3d_001",
        "description": "Identify 3D shapes by counting faces, edges, and vertices",
        "year_level": 4,
        "domain": "Geometry",
        "prerequisites": ["yr3_shape_2d_001"],
        "difficulty_levels": [1, 2, 3, 4],
        "common_misconceptions": [
            "Confusing faces and edges",
            "Counting hidden faces incorrectly"
        ]
    },
]

YEAR_5_GEOMETRY = [
    {
        "skill_id": "yr5_angles_001",
        "description": "Find unknown angle in complementary or supplementary pair",
        "year_level": 5,
        "domain": "Geometry",
        "prerequisites": ["yr4_angles_001"],
        "difficulty_levels": [2, 3, 4, 5],
        "common_misconceptions": [
            "Mixing complementary (sum 90) and supplementary (sum 180)",
            "Subtracting from 360 instead of 90 or 180"
        ]
    },
    {
        "skill_id": "yr5_coords_001",
        "description": "Plot and read coordinates in the first quadrant",
        "year_level": 5,
        "domain": "Geometry",
        "prerequisites": [],
        "difficulty_levels": [1, 2, 3, 4],
        "common_misconceptions": [
            "Swapping x and y coordinates",
            "Starting count from 1 instead of 0 at the origin"
        ]
    },
]


# =============================================================================
# Statistics & Probability Skills (Year 3-5)
# =============================================================================

YEAR_3_STATS = [
    {
        "skill_id": "yr3_data_read_001",
        "description": "Read values from a simple column or picture graph",
        "year_level": 3,
        "domain": "Statistics",
        "prerequisites": [],
        "difficulty_levels": [1, 2, 3],
        "common_misconceptions": [
            "Reading the wrong axis",
            "Counting the category label instead of the value"
        ]
    },
]

YEAR_4_STATS = [
    {
        "skill_id": "yr4_data_interpret_001",
        "description": "Interpret data tables to find totals and largest/smallest",
        "year_level": 4,
        "domain": "Statistics",
        "prerequisites": ["yr3_data_read_001"],
        "difficulty_levels": [1, 2, 3, 4],
        "common_misconceptions": [
            "Confusing largest count with longest category name",
            "Forgetting to add all entries when finding the total"
        ]
    },
    {
        "skill_id": "yr4_chance_001",
        "description": "Classify likelihood of events as impossible, unlikely, likely, or certain",
        "year_level": 4,
        "domain": "Statistics",
        "prerequisites": [],
        "difficulty_levels": [1, 2, 3],
        "common_misconceptions": [
            "Treating 'unlikely' as the same as 'impossible'",
            "Treating 'likely' as the same as 'certain'"
        ]
    },
]

YEAR_5_STATS = [
    {
        "skill_id": "yr5_data_avg_001",
        "description": "Compute the mean (average) of a list of whole numbers",
        "year_level": 5,
        "domain": "Statistics",
        "prerequisites": ["yr4_data_interpret_001", "yr4_mult_div_001"],
        "difficulty_levels": [2, 3, 4, 5],
        "common_misconceptions": [
            "Dividing by the wrong count of numbers",
            "Adding the count to the sum instead of dividing"
        ]
    },
    {
        "skill_id": "yr5_chance_001",
        "description": "Express probability of simple events as a fraction",
        "year_level": 5,
        "domain": "Statistics",
        "prerequisites": ["yr4_chance_001", "yr3_frac_intro_001"],
        "difficulty_levels": [2, 3, 4, 5],
        "common_misconceptions": [
            "Using total outcomes as the numerator",
            "Not reducing equivalent fractions (acceptable here, raw form is fine)"
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
