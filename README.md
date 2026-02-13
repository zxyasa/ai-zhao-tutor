# MathCoach - AI Math Training System

Full-stack AI-powered math training platform for Australian Year 3-6 students (NSW curriculum).

## Architecture

```
mathcoach/
├── apps/ios/              # SwiftUI iPad app
├── services/
│   ├── api/               # FastAPI backend
│   └── content/           # Content generation service
├── packages/shared/       # Shared Pydantic schemas
├── ops/docker/            # Docker configuration
└── docs/                  # Documentation
```

## Quick Start

### Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose**
- **Xcode 15+** (for iOS app development)

### 1. Start Backend Services

```bash
cd ops/docker
docker-compose up -d
```

This starts:
- PostgreSQL database (port 5432)
- FastAPI server (port 8000)

Check health:
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

### 2. Generate Content

```bash
cd services/content
python generate_items.py
python validate_items.py
```

This generates:
- `output/skill_tree_v0.json` - NSW curriculum skill tree
- `output/content_pack_v0.json` - 300+ math items

### 3. Load Content into Database

```bash
cd services/api
python -c "
import json
import sys
sys.path.append('.')
from app.database import SessionLocal
from app.models import Item

with open('../content/output/content_pack_v0.json') as f:
    items_data = json.load(f)

db = SessionLocal()
for item_data in items_data:
    item = Item(
        id=item_data['item_id'],
        skill_id=item_data['skill_id'],
        question_text=item_data['question_text'],
        question_type=item_data['question_type'],
        difficulty=item_data['difficulty'],
        parameters=item_data['parameters'],
        correct_answer=item_data['correct_answer'],
        hint=item_data['hint'],
        explanation=item_data['explanation'],
        validation_rule=item_data['validation_rule']
    )
    db.add(item)
db.commit()
print(f'Loaded {len(items_data)} items into database')
"
```

### 4. Test API

```bash
# Get next item for a student
curl "http://localhost:8000/api/v1/next-item?student_id=test_student_001"

# API documentation
open http://localhost:8000/docs
```

### 5. Run iOS App

```bash
cd apps/ios
open MathCoach.xcodeproj
```

Then:
1. Select iPad simulator
2. Build and run (⌘R)
3. App will connect to http://localhost:8000

## API Endpoints

### GET /api/v1/next-item
Fetch next question for a student based on their mastery level.

**Query Parameters:**
- `student_id` (required): Student identifier
- `skill_id` (optional): Specific skill to practice

**Example:**
```bash
curl "http://localhost:8000/api/v1/next-item?student_id=student_123&skill_id=yr3_frac_compare_001"
```

### POST /api/v1/events
Submit a student answer and update mastery.

**Request Body:**
```json
{
  "event_id": "evt_001",
  "student_id": "student_123",
  "item_id": "yr3_frac_compare_001_d1_1234",
  "answer_given": "3/5",
  "is_correct": true,
  "time_spent": 12.5,
  "hint_requested": false,
  "timestamp": "2024-02-13T10:30:00"
}
```

### POST /api/v1/placement/start
Start a placement test for a student.

**Query Parameters:**
- `student_id`: Student identifier
- `year_level`: Year level (3-6)

Returns a sequence of 10 items across different difficulties.

### GET /api/v1/mastery/{student_id}
Get student's mastery data for all attempted skills.

## Content Service

### Skill Tree
NSW-aligned skills for Year 3-6, focusing on:
- **Fractions**: Introduction, comparison, operations, equivalence
- **Number & Algebra**: Place value, operations, decimals, percentages

Total: **20 skills** across 4 year levels

### Item Templates
- **Fraction Comparison**: Compare two fractions
- **Fraction Addition**: Add two fractions
- **Equivalent Fractions**: Find/simplify equivalent fractions

Each template generates items across 5 difficulty levels.

### Generation
```bash
cd services/content
python generate_items.py
```

Output: `300+ deterministic math items`

### Validation
```bash
python validate_items.py
```

Recomputes all answers to verify correctness.

## Development

### Local API Development

```bash
cd services/api
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Local Content Development

```bash
cd services/content
pip install -r requirements.txt
python generate_items.py
```

### Database Schema

**Models:**
- `Student`: Student profile (id, name, year_level, created_at)
- `Item`: Math questions (id, skill_id, question_text, difficulty, parameters, answer, hint, explanation)
- `Event`: Answer submissions (id, student_id, item_id, answer_given, is_correct, time_spent)
- `Mastery`: Progress tracking (student_id, skill_id, attempts, correct_attempts, mastery_score)

### Stop Services

```bash
cd ops/docker
docker-compose down
```

To remove data:
```bash
docker-compose down -v
```

## Project Structure

```
mathcoach/
├── apps/
│   └── ios/                              # iOS SwiftUI app
│       ├── MathCoach/
│       │   ├── App/                      # App entry point
│       │   ├── Models/                   # Data models
│       │   ├── ViewModels/               # Business logic
│       │   ├── Views/                    # UI screens
│       │   │   └── Components/           # Reusable components
│       │   ├── Services/                 # API client, storage
│       │   └── Utilities/                # Helpers
│       └── README.md
│
├── services/
│   ├── api/                              # FastAPI backend
│   │   ├── app/
│   │   │   ├── models/                   # SQLAlchemy models
│   │   │   ├── routers/                  # API endpoints
│   │   │   ├── database.py               # DB config
│   │   │   ├── config.py                 # Settings
│   │   │   └── main.py                   # FastAPI app
│   │   ├── requirements.txt
│   │   └── README.md
│   │
│   └── content/                          # Content generation
│       ├── curriculum/                   # Skill tree definitions
│       ├── templates/                    # Item templates
│       ├── output/                       # Generated content
│       ├── generate_items.py
│       ├── validate_items.py
│       └── README.md
│
├── packages/
│   └── shared/                           # Shared schemas
│       ├── schemas/
│       │   ├── skill.py
│       │   ├── item.py
│       │   ├── event.py
│       │   └── mastery.py
│       └── setup.py
│
├── ops/
│   └── docker/
│       ├── docker-compose.yml
│       ├── api.Dockerfile
│       └── content.Dockerfile
│
├── docs/
│   ├── prd/                              # Product requirements
│   ├── curriculum/                       # Curriculum alignment
│   └── qa/                               # Testing checklists
│
└── README.md
```

## Tech Stack

- **Backend**: FastAPI, PostgreSQL, SQLAlchemy, Pydantic
- **Content**: Python 3.11, deterministic math generators
- **Frontend**: SwiftUI, MVVM architecture
- **Infrastructure**: Docker, Docker Compose

## Design Principles

- ✅ **No overengineering**: Simple, direct solutions
- ✅ **Modular**: Clear separation of concerns
- ✅ **Deterministic**: All math is reproducible
- ✅ **Testable**: Each component independently verifiable
- ✅ **Minimal UI**: Functional over fancy

## Next Steps

1. **iOS App Implementation** - Build SwiftUI views and ViewModels
2. **Additional Templates** - Expand to all 20 skills
3. **Advanced Features** - Adaptive learning algorithms
4. **Testing** - Unit tests, integration tests
5. **Deployment** - Production infrastructure

## License

Copyright © 2024 MathCoach. All rights reserved.
