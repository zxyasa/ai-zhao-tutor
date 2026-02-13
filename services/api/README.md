# MathCoach API

FastAPI backend service for MathCoach platform.

## Features

- **Item Management**: Fetch next question based on student mastery
- **Event Tracking**: Record student answers and update mastery
- **Placement Testing**: Generate placement test sequences
- **Mastery Dashboard**: Retrieve student progress data

## Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Database

Create `.env` file:

```env
DATABASE_URL=sqlite:///./mathcoach.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://mathcoach:password@localhost:5432/mathcoach
```

### Run Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access API Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### GET /api/v1/next-item

Fetch next item for a student.

**Parameters:**
- `student_id` (required): Student identifier
- `skill_id` (optional): Specific skill to practice

**Response:**
```json
{
  "item_id": "item_001",
  "skill_id": "yr3_frac_compare_001",
  "question_text": "Which is larger: 3/5 or 2/5?",
  "question_type": "fraction",
  "difficulty": 1,
  "parameters": {"num1": 3, "num2": 2, "denom": 5},
  "correct_answer": "3/5",
  "hint": "Compare numerators when denominators are the same",
  "explanation": "...",
  "validation_rule": "exact_match"
}
```

### POST /api/v1/events

Submit student answer event.

**Request Body:**
```json
{
  "event_id": "evt_001",
  "student_id": "student_123",
  "item_id": "item_001",
  "answer_given": "3/5",
  "is_correct": true,
  "time_spent": 12.5,
  "hint_requested": false,
  "timestamp": "2024-02-13T10:30:00"
}
```

### POST /api/v1/placement/start

Start placement test.

**Parameters:**
- `student_id`: Student identifier
- `year_level`: Year level (3-6)

**Response:**
```json
{
  "student_id": "student_123",
  "year_level": 3,
  "items": [...],
  "total_items": 10
}
```

### GET /api/v1/mastery/{student_id}

Get student mastery data.

**Response:**
```json
[
  {
    "student_id": "student_123",
    "skill_id": "yr3_frac_compare_001",
    "total_attempts": 10,
    "correct_attempts": 8,
    "mastery_score": 0.8,
    "last_updated": "2024-02-13T10:30:00"
  }
]
```

## Database Models

- **Student**: Student profile
- **Item**: Question/problem instances
- **Event**: Answer submission records
- **Mastery**: Skill mastery tracking
