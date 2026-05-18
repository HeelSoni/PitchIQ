# 📚 PitchIQ
### AI-Powered Shark Tank India Quantitative Analytics Platform (Seasons 1–5)

---

🌟 **What is PitchIQ?**
PitchIQ is a full-stack, state-of-the-art technical analytics platform that transforms how users interact with academic financial data from **Shark Tank India (Seasons 1–5)**. Powered by reconciled real-world quantitative records parsed from pitch histories, PitchIQ eliminates biological greens and generic colors in favor of a breathtaking, futuristic **Neon Cyan (`#00F2FE`)** and **Space Steel Charcoal (`#080D1A`)** technical style.

Built for data analysts, finance students, and fans of the show, PitchIQ enables serious researchers to trigger side-by-side startup battles, examine macro-financial health indicators, search detailed shark investment portfolios, review complex dilution structures, and query an integrated AI-Powered Analyst Chatbot.

---

## ✨ Core Features

### 🔍 1. High-Performance Startup Directory
* Search over **780+ real startups** with live debounced filtering.
* Filter by **Season**, **Funding Result**, **Profitable State**, **Revenue thresholds (>1CR)**, and **Gross Operating Margins (>30%)**.
* High-contrast glassmorphic badges displaying startup sector, season, and capital terms.

### 📈 2. Dynamic Financial Dashboard
* Macro Recharts area charts visualizing the trend of **Average Startup Revenue** and **Net Profitability** over seasons.
* Operating vs. Gross Margin curves showing macro profitability shifts.
* Side-by-side bar chart representing **Valuation Gap** (Asked vs. Secured) for top-funded deals.

### ⚔️ 3. Side-by-Side Startup Comparison
* Interactive quantitative battlefield allowing side-by-side analysis of any 2 startups.
* Automatically compares revenue, profit margins, capital asked, capital secured, and investment health scores.
* Highlights the **analytical winner** of each category with golden milestone badges.

### 🏆 4. Record Hall of Fame Leaderboard
* Live leaderboards showing top financial performers across seasons:
  * **Top Valued Deals**
  * **Highest Revenue Generation**
  * **Most Active Investors** (highest total ticket size)
  * **Highest EBITDA Margin Leaders**

### 🦈 5. Shark Investment Portfolio Grid
* Interactive profiles for active Sharks (Aman Gupta, Namita Thapar, Peyush Bansal, Ashneer Grover, etc.).
* Displays dynamically calculated key aggregates: **Total Invested Lakhs**, **Average Ticket Size**, **Average Equity Taken**, and **Top 3 Favorite Industries**.
* Full portfolio list displaying all startups backed by the selected shark with investment amounts and equity.

### 📚 6. Financial Glossary & Knowledge Hub
* Contains **17 financial glossary metrics** (EBITDA, Net Profit, Gross Margin, Burn Rate, Runway, etc.) critical to venture capital.
* Features formal mathematical definitions alongside **actual case-study examples** from Shark Tank India pitches.

### 💾 7. Zero-Login CSV Download Hub
* Gives researchers and students the raw parsed database in one click.
* Allows live custom filtering by season, industry, or investment status directly inside the download hub.
* Exports clean, formatted CSV datasets.

### 🤖 8. Context-Aware AI Analyst Assistant
* Floating AI Chatbot that answers questions about deal structures, financial definitions, or specific pitch details.
* Reads database records and falls back intelligently to free Hugging Face LLM models to provide natural language insights.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│               Frontend (Vercel)              │
│   React 19 + Vite + Tailwind CSS v4          │
│   Zustand (State) • Recharts (Visuals)      │
└──────────────────────┬──────────────────────┘
                       │ HTTPS (REST API)
┌──────────────────────▼──────────────────────┐
│              Backend (Railway)               │
│   FastAPI + SQLAlchemy + SQLite / Postgres   │
│   ┌─────────────┐   ┌──────────────────┐   │
│   │  sharks.py  │   │     chat.py      │   │
│   │ (Portfolios │   │  (AI Analyst,    │   │
│   │  & Metrics) │   │   Mistral LLM)   │   │
│   └─────────────┘   └────────┬─────────┘   │
│   ┌─────────────┐            │             │
│   │ startups.py │            │             │
│   │ (Directory, │            │             │
│   │  Compare)   │            │             │
│   └─────────────┘            │             │
└──────────────────────────────┼──────────────┘
                               │ HTTPS
┌──────────────────────────────▼──────────────┐
│            External LLM API (Optional)      │
│  🤗 Hugging Face Inference API (Mistral-7B) │
└─────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 19 + Vite | UI Library & Dev Tooling |
| **Styling** | Tailwind CSS v4 + HSL Custom Palettes | High-Tech Theme System |
| **State** | Zustand | Global React Store & API Synchronization |
| **Charts** | Recharts (SVG) | Custom SVG Financial Dashboards |
| **Backend** | FastAPI (Python) | High-Speed Async REST API Server |
| **Database** | SQLite / PostgreSQL | Structured Relational Pitch Datasets |
| **ORM** | SQLAlchemy | Python Object Relational Mapper |
| **AI LLM** | Mistral-7B-Instruct (HuggingFace) | Free-tier natural language chatbot responses |
| **Data Engine** | Pandas | High-speed data aggregation and statistical wins |

---

## 🚀 Getting Started

### Prerequisites
* **Python 3.10+**
* **Node.js 18+**
* An optional free HuggingFace API key (for Mistral LLM chat responses)

### 1. Backend Server Setup
From the root workspace folder:
```bash
# Initialize Python virtual environment
python -m venv venv
venv\Scripts\activate

# Install all backend packages
pip install -r backend/requirements.txt

# Run the automated data loader (reads CSV -> populates SQLite database)
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

## 📡 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/health` | Server status and database connectivity check |
| **GET** | `/api/startups/` | Retrieve and filter full startups list (supports search, industry, margin thresholds) |
| **GET** | `/api/startups/stats` | Macro aggregate pitch counts, success rates, and total investment figures |
| **GET** | `/api/startups/industries` | List all unique sector industries for directory filters |
| **GET** | `/api/startups/detail/{slug}` | Deep financial breakdown, deal history, cofounders, and computed health score |
| **GET** | `/api/startups/compare` | Trigger side-by-side battlefield comparing two startups |
| **GET** | `/api/sharks/` | List all Sharks and dynamic summary statistics |
| **GET** | `/api/sharks/{shark_id}` | Retrieve individual Shark biography and dynamic backed portfolio grid |
| **GET** | `/api/download/csv` | Stream filtered relational CSV dataset on demand |
| **POST** | `/api/chat/` | Query the PitchIQ AI Chatbot with direct SQLite data context |
| **GET** | `/api/analytics/dashboard` | Aggregated averages, margins, and asked-to-secured valuation gaps by season |
| **GET** | `/api/analytics/leaderboard` | Hall of Fame leaderboard metrics for highest revenues, active sharks, and valuations |

---

## 📂 Project Structure

```
PitchIQ/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── analytics.py   # Dashboard & Hall of Fame aggregates
│   │   │   ├── chat.py        # Context-aware AI Analyst Chatbot
│   │   │   ├── download.py    # Live CSV exporter
│   │   │   ├── sharks.py      # Shark portfolios & aggregates
│   │   │   └── startups.py    # Directory & Side-by-Side Battles
│   │   ├── data/
│   │   │   ├── Shark Tank India.csv  # Reconciled parsed dataset
│   │   │   └── sharks.json    # Shark biography configurations
│   │   ├── models/
│   │   │   └── models.py      # SQLAlchemy schemas (Startups, Deals, Financials)
│   │   ├── services/
│   │   │   ├── health.py      # Formulaic 0-100 Startup Health Score
│   │   │   └── insights.py    # Auto-insights compiler
│   │   ├── main.py            # FastAPI main entrypoint
│   │   └── database.py        # SQLite/Postgres DB session managers
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AIChat.tsx     # Formatted markdown floating chat UI
│   │   │   └── Navbar.tsx     # Sleek sticky tech header navigation
│   │   ├── pages/
│   │   │   ├── ComparePage.tsx            # Quantitative battlefield view
│   │   │   ├── DatasetDownloadPage.tsx    # Filtered exporter hub
│   │   │   ├── DealBreakdownPage.tsx      # Dilution and round terms list
│   │   │   ├── FinancialDashboardPage.tsx # Recharts SVG dashboard
│   │   │   ├── GlossaryPage.tsx           # Ratio definitions & examples
│   │   │   ├── HomePage.tsx               # Debounced search & directories
│   │   │   ├── LeaderboardPage.tsx        # High-performer milestones
│   │   │   ├── SharksPage.tsx             # Interactive Shark portfolios
│   │   │   └── StartupProfilePage.tsx     # Deep health stats & financials
│   │   └── store/
│   │       └── usePitchStore.ts           # State synchronizer
│   ├── index.html
│   └── package.json
└── README.md
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the LICENSE file for details.

Built with ❤️ by **Heel Soni**

*If you found this database tool helpful, please ⭐ star the repo!*
