# PitchIQ — Shark Tank India Analytics Platform (Season 1–5)

PitchIQ is a production-ready, beautiful, and interactive analytics platform for **Shark Tank India (Seasons 1–5)**, powered by actual quantitative records parsed from real pitch history. 

---

## 🚀 Key Features

1. **🏠 Interactive Home Page**: Instant debounced search and filtering by season, funded/rejected status, profitability thresholds, and gross margins.
2. **📈 Financial Dashboard**: Stunning macro charts (using Recharts) for revenue averages, profit metrics, and margin curves.
3. **🤝 Deal Breakdown & Dilution Analysis**: Card grid outlining actual deal splits, dilution ratios, and valuation changes.
4. **📊 Side-by-Side Startup Comparison**: Interactive quantitative battlefield displaying metric highlights and identifying the analytical winner.
5. **🏆 Record Hall of Fame**: Gold-tier milestones listing the biggest deals, highest revenues, most active sharks, and best EBITDA margins.
6. **Meet the Sharks**: Dynamically calculated portfolio grids, average ticket sizes, and top 3 industries invested in by each shark.
7. **📚 Financial Glossary**: Full glossary of 17 financial ratios complete with definitions and real Shark Tank pitch examples.
8. **💾 Filtered CSV Download Hub**: Allows serious analysts to filter and instantly download the reconciled dataset in one click, without login requirements.
9. **🤖 Floating AI Analyst Assistant**: A natural language chatbot that answers complex questions (e.g., about EBITDA, specific valuations like Skippi Ice Pops, or Aman Gupta investment trends) using our database context, with a free HuggingFace API model fallback.

---

## 🛠️ Technology Stack

- **Frontend**: React + Vite + Tailwind CSS v4 + Zustand + Recharts + Lucide Icons.
- **Backend**: FastAPI + SQLAlchemy (ORM) + Pandas + Uvicorn.
- **Database**: PostgreSQL (with automated, zero-config local SQLite fallback).
- **Data Source**: Real-time parsed CSV `backend/app/data/Shark Tank India.csv` containing 789 startup entries.

---

## 💻 Local Development Setup

### 1. Backend Server Setup
From the root workspace folder:
```bash
# Initialize Python virtual environment
python -m venv venv
venv\Scripts\activate

# Install all backend packages
pip install -r backend/requirements.txt

# Run the automated data loader (reads CSV -> populates SQLite/Postgre database)
$env:PYTHONPATH="backend"; venv\Scripts\python backend/app/scripts/seed.py

# Start the FastAPI server (Runs on port 8000)
$env:PYTHONPATH="backend"; venv\Scripts\python -m uvicorn backend.app.main:app --reload --port 8000
```

### 2. Frontend Setup
From the root workspace folder:
```bash
# Navigate to frontend folder
cd frontend

# Install node dependencies
npm install

# Start Vite hot-reloading development server (Runs on http://localhost:5173)
npm run dev
```

---

## 🐳 Running with Docker
If you have Docker installed, simply run:
```bash
docker-compose up --build
```
This spins up a PostgreSQL container, mounts the data volume, imports the real dataset, and exposes the API on `http://localhost:8000` automatically.

---

## 🚀 Cloud Deployment Instructions

### Frontend (Vercel)
The directory contains a custom `vercel.json` file configuring SPA routing:
- Connect your GitHub repo to **Vercel**.
- Set the root directory to `frontend`.
- Set Build Command to `npm run build` and Output Directory to `dist`.
- Click deploy!

### Backend (Render)
The directory contains a custom `render.yaml` configuration:
- Go to Render and create a **Blueprint Instance**.
- Link your repository. Render will automatically configure the PostgreSQL database and FastAPI service.
- Add your optional `HUGGINGFACE_API_KEY` to the environment variables if you want Mistralai LLM generation in your chatbot!
