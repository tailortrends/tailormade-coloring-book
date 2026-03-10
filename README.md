# TailorMadeColoringBook

A web application that allows parents to create personalized coloring books for their children featuring custom characters.

## Tech Stack

- **Frontend**: Vue 3, Vite, Pinia, Tailwind CSS
- **Backend**: FastAPI, Uvicorn, Pydantic
- **Database**: Supabase (PostgreSQL)
- **AI/ML**: OpenCV, Scikit-image (for sketch conversion)
- **Storage**: Firebase Storage

## Setup

### Prerequisites

- Node.js (v18+)
- Python (v3.10+)
- pnpm

### 1. Backend Setup

```bash
# Create and activate virtual environment
python3 -m venv backend/.venv
source backend/.venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run the server
uv run uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
# Install dependencies
pnpm install

# Run the development server
pnpm run dev
```

## Project Structure

```
tailormadecoloringbook/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   ├── main.py       # App entry point
│   │   └── ...
│   ├── requirements.txt  # Python dependencies
│   └── ...
├── frontend/             # Vue frontend
│   ├── src/
│   │   ├── api/          # API clients
│   │   ├── components/   # Vue components
│   │   ├── stores/       # Pinia stores
│   │   ├── views/        # Page views
