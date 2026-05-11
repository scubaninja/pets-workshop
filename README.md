# MatchMyMutt

A fictional dog shelter application with a [Flask](https://flask.palletsprojects.com/en/stable/) backend using [SQLAlchemy](https://www.sqlalchemy.org/) and an [Astro](https://astro.build/) frontend using [Tailwind CSS](https://tailwindcss.com/).

## Features

- **Dog Listings** — Browse available dogs with pagination
- **Dog Details** — View individual dog profiles with breed, age, and description
- **Staff Authentication** — Secure login with hashed passwords (Werkzeug PBKDF2)
- **AI Listing Agent** — Upload pet images and generate SEO-optimized adoption listings using GPT-4o Vision
- **Mock AI Mode** — Offline demo mode with realistic sample responses

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Astro 6, Tailwind CSS 4, TypeScript |
| Backend | Flask, SQLAlchemy, SQLite |
| AI | OpenAI GPT-4o Vision (optional) |
| Testing | Playwright (E2E), pytest (unit) |

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 20+

### Running Locally

1. **Start the backend** (runs on `http://localhost:5100`):
   ```bash
   cd app/scripts
   ./start-app.ps1   # Windows
   ./start-app.sh    # Linux/macOS
   ```

2. **Start the frontend** (runs on `http://localhost:4321`):
   ```bash
   cd app/client
   npm install
   npm run dev
   ```

3. **Seed the database** (optional):
   ```bash
   cd app/scripts
   ./seed-database.ps1   # Windows
   ./seed-database.sh    # Linux/macOS
   ```

### Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for live AI mode |
| `MOCK_AI` | Set to `true` for offline mock responses |
| `FLASK_SECRET_KEY` | Session secret (change in production) |

## Project Structure

```
app/
├── client/           # Astro frontend
│   ├── src/
│   │   ├── pages/    # Routes (index, login, upload, about, dog/[id])
│   │   ├── components/
│   │   └── lib/      # API utilities
│   └── e2e-tests/    # Playwright tests
└── server/           # Flask backend
    ├── app.py        # Main application
    ├── models/       # SQLAlchemy models (Dog, Breed, User)
    ├── services/     # AI listing service
    └── utils/        # Database seeding scripts
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/dogs` | GET | List dogs (paginated) |
| `/api/dogs/<id>` | GET | Get dog details |
| `/api/dogs` | POST | Create dog (staff only) |
| `/api/listing-agent/analyze` | POST | Analyze pet image with AI (staff only) |
| `/api/auth/login` | POST | Staff login |
| `/api/auth/logout` | POST | Logout |
| `/api/auth/me` | GET | Get current user |

## License 

This project is licensed under the terms of the MIT open source license. Please refer to the [LICENSE](./LICENSE) for the full terms.

## Maintainers 

You can find the list of maintainers in [CODEOWNERS](./.github/CODEOWNERS).

## Support

This project is provided as-is, and may be updated over time. If you have questions, please open an issue.
