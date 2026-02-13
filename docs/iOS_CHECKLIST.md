# iOS App Development Checklist

完整的 iOS 应用实施清单,按优先级排序。

## Phase 1: Project Setup (30 分钟)

### Create Xcode Project
- [ ] Open Xcode
- [ ] Create new project: App
- [ ] Product Name: MathCoach
- [ ] Organization: Your Name
- [ ] Interface: SwiftUI
- [ ] Language: Swift
- [ ] Platform: iPad
- [ ] Minimum Deployment: iOS 15.0
- [ ] Save to: `mathcoach/apps/ios/`

### Project Configuration
- [ ] Set deployment target: iPad only
- [ ] Supported orientations: Portrait + Landscape
- [ ] Enable "Supports multiple windows": No
- [ ] App icon: Use placeholder for now

## Phase 2: Data Models (45 分钟)

Create folder: `MathCoach/Models/`

### Student.swift
```swift
struct Student: Codable, Identifiable {
    let id: String
    let name: String
    let yearLevel: Int
    let createdAt: Date
}
```

### Item.swift
```swift
struct Item: Codable, Identifiable {
    let id: String
    let skillId: String
    let questionText: String
    let questionType: String
    let difficulty: Int
    let parameters: [String: AnyCodable]
    let correctAnswer: String
    let hint: String
    let explanation: String

    enum CodingKeys: String, CodingKey {
        case id = "item_id"
        case skillId = "skill_id"
        case questionText = "question_text"
        case questionType = "question_type"
        // ...
    }
}
```

### Event.swift
```swift
struct Event: Codable {
    let eventId: String
    let studentId: String
    let itemId: String
    let answerGiven: String
    let isCorrect: Bool
    let timeSpent: Double
    let hintRequested: Bool
    let timestamp: Date
}
```

### Mastery.swift
```swift
struct Mastery: Codable {
    let studentId: String
    let skillId: String
    let totalAttempts: Int
    let correctAttempts: Int
    let masteryScore: Double
    let lastUpdated: Date
}
```

### AnyCodable.swift (Helper)
```swift
struct AnyCodable: Codable {
    let value: Any
    // Implementation for JSON decoding
}
```

## Phase 3: Services Layer (1 小时)

### APIClient.swift
- [ ] Create `Services/APIClient.swift`
- [ ] Define `APIClientProtocol`
- [ ] Implement `APIClient` class
- [ ] Methods:
  - `fetchNextItem(studentId:skillId:) async throws -> Item`
  - `submitEvent(_ event:) async throws`
  - `startPlacement(studentId:yearLevel:) async throws -> [Item]`
  - `fetchMastery(studentId:) async throws -> [Mastery]`
- [ ] Retry logic (3 attempts, exponential backoff)
- [ ] Error handling: `NetworkError` enum

### StorageService.swift
- [ ] UserDefaults wrapper
- [ ] Methods:
  - `saveStudent(_ student: Student)`
  - `loadStudent() -> Student?`
  - `saveAnswerHistory(_ answers: [Event])`
  - `loadAnswerHistory() -> [Event]`

### MockAPIClient.swift (optional for testing)
- [ ] Implement `APIClientProtocol`
- [ ] Return hardcoded sample data
- [ ] Use for offline testing

## Phase 4: Utilities (30 分钟)

### TimeTracker.swift
```swift
class TimeTracker: ObservableObject {
    @Published var elapsedTime: TimeInterval = 0
    private var startTime: Date?

    func start()
    func stop() -> TimeInterval
    func reset()
}
```

### NetworkMonitor.swift (optional)
```swift
class NetworkMonitor: ObservableObject {
    @Published var isConnected: Bool = true
    // Use Network framework
}
```

## Phase 5: Custom Components (1 小时)

### FractionInputView.swift
- [ ] Create `Views/Components/FractionInputView.swift`
- [ ] Two TextField: numerator + denominator
- [ ] Layout: `[___] / [___]`
- [ ] Validation: numbers only
- [ ] @Binding for numerator and denominator
- [ ] Formatted output callback

```swift
struct FractionInputView: View {
    @Binding var numerator: String
    @Binding var denominator: String

    var body: some View {
        HStack {
            TextField("Top", text: $numerator)
                .keyboardType(.numberPad)
            Text("/")
            TextField("Bottom", text: $denominator)
                .keyboardType(.numberPad)
        }
    }
}
```

### LoadingView.swift (optional)
Simple loading spinner component

## Phase 6: ViewModels (2.5 小时)

### HomeViewModel.swift
- [ ] `@Published var student: Student?`
- [ ] `@Published var isLoading: Bool`
- [ ] `func loadOrCreateStudent()`
- [ ] `func startPlacementTest()`
- [ ] `func startPractice()`

### PracticeViewModel.swift
- [ ] `@Published var currentItem: Item?`
- [ ] `@Published var userAnswer: String`
- [ ] `@Published var showHint: Bool`
- [ ] `@Published var isSubmitting: Bool`
- [ ] `@Published var errorMessage: String?`
- [ ] `@StateObject var timeTracker: TimeTracker`
- [ ] `func fetchNextItem()`
- [ ] `func submitAnswer()`
- [ ] `func requestHint()`

### ResultViewModel.swift
- [ ] `@Published var events: [Event]`
- [ ] `@Published var score: (correct: Int, total: Int)`
- [ ] `func calculateResults()`

### MasteryDashboardViewModel.swift
- [ ] `@Published var masteryData: [Mastery]`
- [ ] `func loadMasteryData()`

## Phase 7: Views (3 小时)

### HomeView.swift
- [ ] Welcome message
- [ ] "Start Placement Test" button
- [ ] "Practice" button
- [ ] "View Progress" button
- [ ] Navigation setup

### PracticeView.swift
- [ ] Question text display
- [ ] Answer input (TextField or FractionInputView)
- [ ] Submit button
- [ ] Hint button
- [ ] Timer display
- [ ] Progress indicator
- [ ] Error banner
- [ ] Navigation to ResultView

### ResultView.swift
- [ ] Score summary
- [ ] Time statistics
- [ ] Question list with ✓/✗
- [ ] Explanation expandable sections
- [ ] "Continue" button

### MasteryDashboardView.swift
- [ ] Skill list
- [ ] Progress bars
- [ ] Color coding (red/yellow/green)
- [ ] Sort by mastery score

### PlacementTestView.swift
- [ ] Similar to PracticeView
- [ ] Fixed sequence of items
- [ ] Progress through all items
- [ ] Navigate to results

## Phase 8: App Entry Point (30 分钟)

### MathCoachApp.swift
- [ ] Setup dependency injection
- [ ] Initialize APIClient
- [ ] Initialize StorageService
- [ ] Root view: HomeView
- [ ] Navigation configuration

```swift
@main
struct MathCoachApp: App {
    @StateObject var apiClient = APIClient()
    @StateObject var storage = StorageService()

    var body: some Scene {
        WindowGroup {
            HomeView()
                .environmentObject(apiClient)
                .environmentObject(storage)
        }
    }
}
```

## Phase 9: Testing (1 小时)

### Manual Testing Checklist
- [ ] Backend running and reachable
- [ ] Fetch next item works
- [ ] Submit answer updates mastery
- [ ] Fraction input accepts valid input
- [ ] Fraction input rejects invalid input
- [ ] Timer starts and stops correctly
- [ ] Hint button shows hint
- [ ] Explanation displays after answer
- [ ] Result view calculates score correctly
- [ ] Mastery dashboard shows progress
- [ ] Offline mode shows error gracefully
- [ ] Retry logic works

### Test Data
Create test student:
```bash
curl -X POST http://localhost:8000/api/v1/students \
  -H "Content-Type: application/json" \
  -d '{"id":"test_student","name":"Test User","year_level":4}'
```

## Phase 10: Polish (30 分钟)

- [ ] Add app icon
- [ ] Add launch screen
- [ ] Improve error messages
- [ ] Add haptic feedback
- [ ] Smooth animations
- [ ] Accessibility labels

## Estimated Total Time: ~11 hours

Realistically over 2-3 evenings:
- **Evening 1**: Phases 1-4 (project setup, models, services, utilities)
- **Evening 2**: Phases 5-7 (components, ViewModels, Views)
- **Evening 3**: Phases 8-10 (integration, testing, polish)

## Tips

- Start with minimal UI - no fancy styling
- Test each ViewModel independently
- Use preview providers for rapid iteration
- Keep API base URL configurable
- Commit frequently

## Reference Files

All architecture details in: `C:\Users\zxyas\.claude\plans\sprightly-giggling-lemon.md`
