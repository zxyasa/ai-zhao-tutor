# MathCoach Development Guide

## Project Overview
Full-stack AI math training system for NSW Year 3-6 students.

## Architecture
- **Monorepo**: All services in one repository
- **Backend**: FastAPI + PostgreSQL
- **Content**: Python generators (deterministic math)
- **Frontend**: SwiftUI iPad app (MVVM)

## Development Workflow

### 1. Backend Changes
```bash
cd services/api
# Make changes to models, routers, etc.
# Test locally:
uvicorn app.main:app --reload
```

### 2. Content Changes
```bash
cd services/content
# Edit curriculum or templates
python generate_items.py
python validate_items.py
```

### 3. Docker Workflow
```bash
cd ops/docker
docker-compose up -d
docker-compose logs -f api
docker-compose down
```

## Coding Standards

### Python
- Use type hints
- Follow PEP 8
- Keep functions small and focused
- Write deterministic code (no randomness in production)

### Database
- Always use migrations for schema changes
- Index foreign keys
- Use transactions for multi-step operations

### API
- RESTful endpoints
- Clear error messages
- Validate all inputs with Pydantic

### Content Generation
- All math must be verifiable
- Include hints and explanations
- Test edge cases

## Common Tasks

### Add a New Skill
1. Add to `services/content/curriculum/nsw_year3_6.py`
2. Create template in `services/content/templates/`
3. Register template in `templates/__init__.py`
4. Run `python generate_items.py`
5. Run `python validate_items.py`

### Add a New API Endpoint
1. Create router in `services/api/app/routers/`
2. Register in `services/api/app/main.py`
3. Test with curl or Swagger UI

### Add a New Database Model
1. Create model in `services/api/app/models/`
2. Update `models/__init__.py`
3. Create migration (if using Alembic)
4. Run migration

## Testing
- Validate all content with `validate_items.py`
- Test API endpoints via `/docs`
- Manual testing on iPad simulator

## Don'ts
- ❌ Don't skip validation
- ❌ Don't hardcode credentials
- ❌ Don't generate random answers
- ❌ Don't break determinism
- ❌ Don't overengineer simple features

## Deployment (Future)
- Use environment variables for config
- PostgreSQL for production
- Docker Compose for staging
- TestFlight for iOS app distribution
