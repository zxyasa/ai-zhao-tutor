# Mac Setup Guide

晚上在 Mac Studio 上继续开发的完整指南。

## Prerequisites

- macOS 12+
- Xcode 15+
- Homebrew
- Python 3.11+
- Docker Desktop for Mac

## Step 1: Clone Repository

```bash
cd ~/Projects  # or your preferred location
git clone https://github.com/YOUR_USERNAME/mathcoach.git
cd mathcoach
```

## Step 2: Install Dependencies

### Install Homebrew (if not installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Install Python 3.11
```bash
brew install python@3.11
python3.11 --version
```

### Install Docker Desktop
Download from: https://www.docker.com/products/docker-desktop/

## Step 3: Backend Setup

### Start Services with Docker
```bash
cd ops/docker
docker-compose up -d

# Check health
curl http://localhost:8000/health
```

### Or run locally without Docker
```bash
# Install API dependencies
cd services/api
pip3.11 install -r requirements.txt

# Run API
uvicorn app.main:app --reload
```

## Step 4: Generate Content

```bash
cd services/content
pip3.11 install -r requirements.txt

# Generate items
python3.11 generate_items.py

# Validate
python3.11 validate_items.py
```

Output:
- `output/skill_tree_v0.json` - 20 skills
- `output/content_pack_v0.json` - 300+ items

## Step 5: Load Content into Database

```bash
cd services/api
python3.11 scripts/load_content.py
```

## Step 6: iOS App Development

### Open Xcode Project
```bash
cd apps/ios
open MathCoach.xcodeproj
```

### Configuration
1. Select iPad simulator (iPad Pro 12.9")
2. Update API base URL if needed:
   - In `APIClient.swift`: `baseURL = "http://localhost:8000/api/v1"`
3. Build and Run (⌘R)

### First Run Checklist
- [ ] Backend running on http://localhost:8000
- [ ] Content generated (300+ items)
- [ ] Database populated with items
- [ ] Xcode project opens successfully
- [ ] iPad simulator selected
- [ ] App builds without errors

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs -f api

# Restart
docker-compose restart api
```

### Content generation fails
```bash
# Check Python version
python3.11 --version

# Reinstall dependencies
pip3.11 install --upgrade -r requirements.txt
```

### Xcode build errors
- Clean build folder: ⇧⌘K
- Delete DerivedData: `rm -rf ~/Library/Developer/Xcode/DerivedData`
- Restart Xcode

## Development Workflow

### Backend Changes
```bash
cd services/api
# Edit code
# Docker auto-reloads with --reload flag
```

### Content Changes
```bash
cd services/content
# Edit templates or curriculum
python3.11 generate_items.py
python3.11 validate_items.py
python3.11 ../api/scripts/load_content.py
```

### iOS Changes
- Edit in Xcode
- ⌘B to build
- ⌘R to run
- Use breakpoints for debugging

## Git Workflow

```bash
# Pull latest changes
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# Commit changes
git add .
git commit -m "Description of changes"

# Push to GitHub
git push origin feature/your-feature-name
```

## Next Steps

1. ✅ Verify backend health
2. ✅ Generate content
3. ✅ Load content into database
4. 🚀 Start iOS app development (see iOS_CHECKLIST.md)
