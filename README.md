# ⚡ PitchIQ — Shark Tank India Analytics Platform (Season 1–5)

PitchIQ is a production-ready, beautiful, and interactive analytics platform for **Shark Tank India (Seasons 1–5)**, powered by actual quantitative records parsed from real pitch history. It provides investors, analysts, and fans with deep financial insights, startup valuations, operational health metrics, and a dynamic AI-powered analyst assistant.

---

## 🚀 Key Features

* **🏠 Interactive Home Directory**: Instant debounced search and filtering by season, funded/rejected status, profitability thresholds, and gross margins.
* **📈 Financial Dashboard**: Stunning macro charts (using Recharts) for average revenues, profit metrics, and operating margin curves.
* **🤝 Deal Breakdown & Dilution Analysis**: Card grid outlining actual deal splits, dilution ratios, and valuation differences.
* **📊 Side-by-Side Startup Comparison**: Interactive quantitative battlefield displaying metric highlights and identifying the statistical winner for each category.
* **🏆 Hall of Fame**: Gold-tier milestones listing the biggest deals, highest revenues, most active sharks, and best EBITDA margins.
* **Meet the Sharks**: Dynamically calculated portfolio grids, average ticket sizes, and top 3 industries invested in by each shark.
* **📚 Financial Glossary**: Full glossary of 17 financial ratios complete with definitions and real Shark Tank pitch examples.
* **💾 Filtered CSV Download Hub**: Allows serious analysts to filter and instantly download the reconciled dataset in one click, without login requirements.
* **🤖 Floating AI Analyst Assistant**: A natural language chatbot that answers complex questions (e.g., about EBITDA, specific valuations like Skippi Ice Pops, or Aman Gupta investment trends) using our database context.

---

## 🛠️ Technical Architecture & Design System

The application is built using a modern decoupled client-server architecture:

```
[ Frontend: React + Vite ] ──(REST API & JSON)──> [ Backend: FastAPI ] ──> [ DB: SQLite / Postgres ]
```

### Client Layer (Frontend)
* **Core**: React 19 + TypeScript + Vite.
* **State Management**: Zustand (lightweight, reactive store).
* **Styling**: Tailwind CSS (Premium Futuristic Neon Cyan & Electric Blue theme).
* **Charts**: Recharts (responsive SVG rendering with custom tooltips).

### Server Layer (Backend)
* **Core**: FastAPI (High-performance asynchronous Python web framework).
* **Data Processing**: Pandas (for high-speed data calculations and stats).
* **ORM**: SQLAlchemy (for database migrations and data querying).

---

## 💻 Local Development Setup

Follow these simple steps to run the complete platform locally on your machine.

### 1. Backend Server Setup
From the root workspace folder:
```bash
# Initialize Python virtual environment
python -m venv venv
venv\Scripts\activate

# Install all backend packages
pip install -r backend/requirements.txt

# Run the automated data loader (reads CSV -> populates database)
$env:PYTHONPATH="backend"; venv\Scripts\python backend/app/scripts/seed.py

# Start the FastAPI server (Runs on port 8000)
$env:PYTHONPATH="backend"; venv\Scripts\python -m uvicorn backend.app.main:app --reload --port 8000
```

### 2. Frontend Setup
From a new terminal starting in the root workspace folder:
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

If you prefer to run the entire application in containers, simply execute:
```bash
docker-compose up --build
```
This spins up the database, imports the real dataset, starts the API backend, and boots the client interface automatically.
