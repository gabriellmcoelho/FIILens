#!/bin/bash

echo "🚀 Setting up FIILens MVP..."

# Backend setup
echo "📦 Installing backend dependencies..."
cd backend
npm install

echo "🗄️  Generating Prisma client..."
npm run prisma:generate

echo "🔄 Running database migrations..."
npm run prisma:deploy

cd ..

# Frontend setup
echo "📦 Installing frontend dependencies..."
cd frontend
npm install

cd ..

# Analytics setup
echo "🐍 Installing Python dependencies..."
cd analytics
pip install -r requirements.txt

echo "📊 Seeding database with sample data..."
python main.py

cd ..

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "1. Backend:  cd backend && npm run dev"
echo "2. Frontend: cd frontend && npm run dev"
echo ""
echo "Backend API: http://localhost:3333"
echo "Frontend:    http://localhost:5173"
echo "API Docs:    http://localhost:3333/docs"
