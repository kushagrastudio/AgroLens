#!/bin/bash

echo "Setting up AgroLens..."

# create virtual environment
python3 -m venv venv
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# copy env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env file created — add your ANTHROPIC_API_KEY before running"
fi

# create folders if not exist
mkdir -p backend/models
mkdir -p backend/knowledge/indexes
mkdir -p data

# download models
echo "Downloading models..."
python scripts/download_model.py

# build FAISS indexes
echo "Building knowledge indexes..."
python scripts/build_indexes.py

# frontend setup
echo "Setting up frontend..."
cd frontend
npm install
cd ..

echo ""
echo "Setup complete."
echo "To start backend:  source venv/bin/activate && uvicorn backend.main:app --reload --port 8000"
echo "To start frontend: cd frontend && npm run dev"