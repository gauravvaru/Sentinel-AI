# Sentinel AI

Sentinel AI is an advanced, real-time analytics dashboard and intelligence platform. It is designed to perform deep behavioral segmentation, influence mapping, narrative tracking, and semantic search on global public conversational data.

## Key Features

- **Topic & Trend Analysis**: Real-time tracking of emerging narratives and conversation velocity.
- **Network Analysis & Influence**: Force-directed interaction graphs and PageRank-based global influence scoring to identify key nodes and communities driving discussions.
- **Audience Cohorts**: Behavioral segmentation and clustering of network participants, grouped by common traits and interaction patterns.
- **Insight Engine**: Automated telemetry analysis to derive insights from recent data windows.
- **Semantic Search**: Vector-based discovery of narratives and influence nodes using natural language queries against event embeddings.
- **Premium B2B Design**: A clean, light-themed, professional dashboard built with a strict visual contract (Stitch v4 design).

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Data & Processing**: Pandas, NumPy, Scikit-learn (ML/Clustering)
- **Architecture**: RESTful APIs, Semantic Search engine, PageRank & Community detection algorithms.

### Frontend
- **Framework**: React 18, TypeScript, Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router (Declarative routing)
- **State/Fetching**: Custom polling hooks mapped to REST endpoints.

## Project Structure

```
Sentinel AI/
├── src/
│   ├── api/          # FastAPI backend routes (insights, network, audience, main.py, etc.)
│   ├── core/         # Backend configuration and core utilities
│   ├── models/       # Data models and ML pipelines
│   └── services/     # Business logic and external integrations
├── frontend/
│   ├── src/          # React frontend source
│   ├── public/       # Static assets
│   ├── package.json  # Frontend dependencies
│   └── vite.config.ts# Vite configuration
├── .env.example      # Environment variables template
└── requirements.txt  # Python backend dependencies
```

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm

### Backend Setup
1. Navigate to the root directory.
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables (copy `.env.example` to `.env` and fill in API keys if required).
5. Run the FastAPI development server:
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   ```

### Frontend Setup
1. Open a new terminal and navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Access the dashboard at `http://localhost:5174/` (or the port specified by Vite). The frontend is configured to proxy `/api` requests to `http://localhost:8000`.

## License
[Proprietary/Internal] - All rights reserved.
