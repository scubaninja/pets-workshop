# MatchMyMutt - AI-Powered Pet Listing Platform

## Demo Summary

**MatchMyMutt** is a pet adoption platform that uses AI (OpenAI GPT-4o Vision) to automatically transform raw pet photos into fully searchable, SEO-optimized adoption listings.

**Key Features Demonstrated:**
1. **Personal Listing Agent** - Staff upload a pet photo with optional notes (name, breed, personality) → AI analyzes the image and generates a complete listing with title, description, personality traits, adoption highlights, SEO keywords, and categories
2. **Auto-create breeds** - If the AI detects a breed not in the database, it's automatically created
3. **Mock mode** - Set `MOCK_AI=true` for offline demos with realistic sample responses
4. **Rich listing display** - Generated listings appear on the homepage with photos, showing traits, categories, and "Why Adopt?" highlights on detail pages

---

## Technical Architecture

### 1. Login / Authorization for Users

**Implementation:** Session-based authentication with role-based access control

```python
# User model with secure password hashing (models/user.py)
class User(BaseModel):
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='staff')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

```python
# Protected routes use @staff_required decorator (app.py)
@staff_required
def analyze_listing():
    # Only authenticated staff can access AI features
```

**Flow:**
- `POST /api/auth/login` - Validates credentials, creates session
- `GET /api/auth/me` - Returns current user from session
- `POST /api/auth/logout` - Clears session
- Protected routes (like `/upload`) redirect unauthenticated users to login

---

### 2. Data Persistence

**Implementation:** SQLAlchemy ORM with SQLite database

**Models:**
- `User` - Staff accounts with hashed passwords
- `Breed` - Pet breeds (auto-created when AI detects new ones)
- `Dog` - Pet listings with AI-generated fields

```python
# Dog model with AI-generated fields (models/dog.py)
class Dog(BaseModel):
    # Basic fields
    name = db.Column(db.String(100), nullable=False)
    breed_id = db.Column(db.Integer, db.ForeignKey('breeds.id'))
    description = db.Column(db.Text)
    
    # AI-generated listing fields
    ai_generated = db.Column(db.Boolean, default=False)
    image_path = db.Column(db.String(500))
    seo_title = db.Column(db.String(200))
    seo_keywords = db.Column(JSON)
    tags = db.Column(JSON)
    traits = db.Column(JSON)
    adoption_highlights = db.Column(JSON)
    categories = db.Column(JSON)
```

**Relationships:**
- `Dog.breed` → `Breed` (with auto-create for new breeds)

---

### 3. Meaningful Tests

**Backend Unit Tests** (`app/server/test_app.py`) - 10 tests:

| Test | Coverage |
|------|----------|
| `test_get_dogs_success` | Retrieval of multiple dogs with AI fields |
| `test_get_dogs_empty` | Empty database returns empty list |
| `test_get_dogs_structure` | Response structure validation |
| `test_login_success` | Valid credentials create session |
| `test_login_invalid_password` | Invalid credentials rejected |
| `test_logout_clears_session` | Logout clears user session |
| `test_me_requires_login` | `/api/auth/me` requires authentication |
| `test_me_returns_current_user` | Returns logged-in user info |
| `test_protected_listing_agent_rejects_guest` | AI endpoints require login |
| `test_protected_listing_agent_rejects_non_staff` | AI endpoints require staff role |

**AI Service Unit Tests** (`app/server/test_ai_service.py`) - 12 tests:

| Test Class | Coverage |
|------------|----------|
| `TestPetAnalysisResult` | Dataclass structure and `to_dict()` method |
| `TestMockResponses` | Mock response validation (required fields, valid values) |
| `TestAnalyzePetImage` | Mock analysis returns proper `PetAnalysisResult` structure |
| `TestImageHelpers` | Base64 encoding, media type detection (JPEG, PNG, GIF, WebP) |

**End-to-End Tests** (Playwright - 25 tests):

| Test File | Coverage |
|-----------|----------|
| `auth.spec.ts` | Login/logout flow, guest vs staff access, protected routes |
| `homepage.spec.ts` | Dog listing display, navigation, pagination |
| `dog-details.spec.ts` | Detail page rendering, AI-generated info display |
| `about.spec.ts` | About page content and navigation |
| `upload.spec.ts` | Personal Listing Agent upload flow, analysis preview |
| `api-integration.spec.ts` | Frontend-backend API communication |

Example auth test:
```typescript
test('staff can log in and reach upload page', async ({ page }) => {
  await page.goto('/login');
  await page.getByTestId('login-submit').click();
  await expect(page).toHaveURL('/upload');
  await expect(page.getByTestId('upload-heading')).toHaveText('Personal Listing Agent');
});
```

---

### 4. Programmatic Use of AI/Codex SDK

**Implementation:** OpenAI GPT-4o Vision API with function calling for structured output

```python
# services/ai_listing_service.py
from openai import OpenAI

def _live_analyze(image_path: str, additional_notes: str = "") -> PetAnalysisResult:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    # Encode image to base64 for Vision API
    image_data = _encode_image_to_base64(image_path)
    
    # Call GPT-4o with vision + function calling
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
                {"type": "text", "text": "Analyze this pet and create an adoption listing."},
                {"type": "text", "text": f"Staff notes: {additional_notes}"}
            ]}
        ],
        functions=[ANALYSIS_FUNCTION],  # Structured output schema
        function_call={"name": "create_pet_listing"}
    )
```

**Key AI Features:**
- **Vision Analysis** - Detects breed, size, age, gender from photo
- **Structured Output** - Function calling ensures consistent JSON schema
- **Context Integration** - Staff notes (name, breed, personality) are incorporated
- **Mock Mode** - `MOCK_AI=true` provides offline demo with realistic responses

---

## How I Built This

### Planning Phase

1. **Defined the core use case**: Staff uploads pet photo → AI generates complete listing
2. **Identified components needed**:
   - Authentication system for staff-only features
   - Image upload and storage
   - OpenAI Vision integration
   - Database schema for AI-generated fields
   - Frontend UI for upload and display

### Execution with Copilot

**Session workflow:**

1. **Created AI Service** (`ai_listing_service.py`)
   - Designed `PetAnalysisResult` dataclass with all listing fields
   - Built mock responses for offline demos
   - Integrated OpenAI SDK with GPT-4o Vision + function calling

2. **Extended Database Schema**
   - Added AI fields to Dog model (seo_title, traits, tags, etc.)
   - Ran migration to add columns to existing table
   - Added breed relationship for auto-create functionality

3. **Built API Endpoints**
   - `POST /api/listing-agent/analyze` - Accepts image, returns AI analysis
   - `POST /api/dogs` - Creates listing from analysis (auto-creates breeds)
   - Protected routes with `@staff_required` decorator

4. **Created Frontend**
   - Upload page with image preview and notes field
   - Live preview of AI-generated listing before saving
   - Homepage cards showing photos for AI-generated listings
   - Detail page with traits, highlights, categories sections

5. **Debugging Iterations**
   - Fixed CORS issues between Astro (4321) and Flask (5100)
   - Created Astro API proxy routes for SSR mode
   - Fixed environment variable handling for mock vs live mode
   - Added relationship fixes for ORM queries

**Tools Used:**
- Flask + SQLAlchemy for backend
- Astro + Tailwind for frontend
- OpenAI SDK (gpt-4o) for AI
- Playwright for E2E tests
- GitHub Copilot for code generation and debugging

---

## Running the Demo

```bash
# Start backend (live AI mode)
cd app/server
$env:OPENAI_API_KEY = "sk-..."
$env:MOCK_AI = "false"
python app.py

# Start frontend
cd app/client
npm run dev

# Login: staff@tailspin.example / TailspinDemo123!
# Navigate to "Upload Listing" → Upload photo → Create Listing
```

---

## Running Tests

```bash
# Backend unit tests (22 tests)
cd app/server
python -m pytest test_app.py test_ai_service.py -v

# E2E tests (25 tests - auto-starts servers if not running)
cd app/client
npx playwright test

# View E2E test report
npx playwright show-report
```
