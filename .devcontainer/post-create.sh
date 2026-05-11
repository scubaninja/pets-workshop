#!/bin/bash
set -e

echo "🐾 Setting up MatchMyMutt development environment..."

# Install Python dependencies for backend
echo "📦 Installing Python dependencies..."
cd app/server
pip install --upgrade pip
pip install -r requirements.txt
pip install openai

# Seed the database
echo "🗄️ Seeding database..."
python -c "from app import app, db; app.app_context().push(); db.create_all()"
python utils/seed_database.py || true

# Install Node.js dependencies for frontend
echo "📦 Installing Node.js dependencies..."
cd ../client
npm install

# Install Playwright for testing
echo "🎭 Installing Playwright..."
npx playwright install --with-deps chromium

echo ""
echo "✅ Development environment ready!"
echo ""
echo "To start the app:"
echo "  Backend:  cd app/server && python app.py"
echo "  Frontend: cd app/client && npm run dev"
echo ""
echo "Environment variables:"
echo "  MOCK_AI=true (default, for offline demos)"
echo "  Set OPENAI_API_KEY for live AI mode"
echo ""
