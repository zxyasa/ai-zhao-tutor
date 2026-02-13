# iOS App Setup Guide

**✅ Status:** Backend完成 | Models prepared | 等待 Xcode 安装

## 🎯 After Xcode Finishes Installing

### Step 1: Verify Xcode Installation

```bash
xcodebuild -version
```

Should show: `Xcode 15.x` or later

### Step 2: Create Xcode Project

1. Open Xcode
2. Click "Create a new Xcode project"
3. Choose **App** template
4. Configuration:
   - **Product Name:** MathCoach
   - **Organization:** Your Name
   - **Interface:** SwiftUI
   - **Language:** Swift
   - **Platform:** iPad
5. Save location: `~/agents/ai-zhao-tutor/apps/ios/`

### Step 3: Add Prepared Model Files

The following files are already created and ready to add:

```
~/agents/ai-zhao-tutor/apps/ios/MathCoach/Models/
├── AnyCodable.swift   ✅ Ready
├── Student.swift      ✅ Ready
├── Item.swift         ✅ Ready
├── Event.swift        ✅ Ready
└── Mastery.swift      ✅ Ready
```

**To add them to Xcode:**
1. Right-click on `MathCoach` folder in Xcode
2. Select "Add Files to MathCoach..."
3. Navigate to `~/agents/ai-zhao-tutor/apps/ios/MathCoach/Models/`
4. Select all `.swift` files
5. Ensure "Copy items if needed" is **unchecked** (files are already in correct location)
6. Click "Add"

### Step 4: Configure Project Settings

1. Select your project in the navigator
2. Select the target "MathCoach"
3. Go to **General** tab:
   - Set **Minimum Deployment:** iOS 15.0
   - **Supported Destinations:** iPad only
4. Go to **Signing & Capabilities**:
   - Select your development team
   - Xcode will auto-manage signing

### Step 5: Test Build

1. Select an iPad simulator (e.g., iPad Pro 12.9")
2. Press **⌘R** to build and run
3. The app should launch (even if it's just a blank screen for now)

## 📁 Project Structure

```
MathCoach/
├── Models/            ✅ Complete (5 files)
│   ├── AnyCodable.swift
│   ├── Student.swift
│   ├── Item.swift
│   ├── Event.swift
│   └── Mastery.swift
├── ViewModels/        🔜 Next phase
├── Views/             🔜 Next phase
├── Services/          🔜 Next phase
│   └── APIClient.swift
└── Utilities/         🔜 Next phase
```

## 🚀 What's Already Working

- ✅ Backend API running on http://localhost:8000
- ✅ PostgreSQL database with 110 math questions
- ✅ All data models defined and ready
- ✅ JSON decoding configured with proper key mapping

## 📝 Next Steps (Phase 3-7)

After the project builds successfully:

1. **Phase 3:** Create `Services/APIClient.swift` for backend communication
2. **Phase 4:** Create ViewModels for business logic
3. **Phase 5:** Create SwiftUI Views for UI
4. **Phase 6:** Test end-to-end flow
5. **Phase 7:** Polish and bug fixes

## 🛠️ Troubleshooting

### Build Error: "Cannot find 'AnyCodable' in scope"
- Make sure all Model files are added to the target
- Check file membership in File Inspector (right panel)

### Simulator Not Showing
- Go to **Xcode → Preferences → Platforms**
- Download iOS simulators if needed

### Backend Not Responding
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not running, restart Docker
cd ~/agents/ai-zhao-tutor/ops/docker
docker-compose up -d
```

## 📊 Backend Status

```bash
# Check backend health
curl http://localhost:8000/health

# Get a test question
curl "http://localhost:8000/api/v1/next-item?student_id=test_001"

# View API documentation
open http://localhost:8000/docs
```

## 🎓 Learning Resources

- [SwiftUI Documentation](https://developer.apple.com/documentation/swiftui)
- [URLSession Networking](https://developer.apple.com/documentation/foundation/urlsession)
- [Codable](https://developer.apple.com/documentation/swift/codable)

---

**Estimated Time to Complete:**
- Phase 3 (Services): 1 hour
- Phase 4 (ViewModels): 1.5 hours
- Phase 5 (Views): 3 hours
- Total: ~5.5 hours

**Total Progress:** 2/7 phases complete (Backend + Models)
