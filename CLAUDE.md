# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EventPredictor (全球局势推演决策系统) is a multi-agent system for analyzing global events and predicting trends. It accepts event data and outputs predictions with confidence scores through a three-stage pipeline: Information Collection → Deep Analysis → Trend Prediction.

## Development Commands

### Backend (Python/FastAPI)

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python main.py                 # Uses config from config.yaml
# Or with uvicorn
uvicorn app.main:app --reload --port 8005

# Run tests
pytest tests/ -v               # All tests
pytest tests/test_api.py -v    # Specific test file
pytest -m unit                 # Unit tests only
pytest -m integration          # Integration tests only

# Run with coverage
pytest --cov=app --cov=api tests/
```

### Frontend (React/TypeScript/Vite)

```bash
cd frontend

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint

# Preview production build
npm run preview
```

### Docker

```bash
# Build and run
docker build -f docker/Dockerfile -t eventpredictor .
docker run -p 8000:8000 eventpredictor

# Or with docker-compose
docker-compose up -d
```

## Architecture

### Backend Structure

```
app/
├── main.py                 # FastAPI application entry point
├── core/
│   └── config.py           # Configuration management (loads from config.yaml)
├── api/
│   ├── routes/             # API endpoints
│   │   ├── predict.py      # POST /api/v1/predict
│   │   ├── events.py       # GET /api/v1/events
│   │   ├── health.py       # GET /health
│   │   └── multi_agent.py  # Multi-agent role analysis
│   └── models/             # Pydantic models for requests/responses
├── agents/
│   ├── pipeline.py         # Agent orchestration (InfoCollector → Analyzer → Predictor)
│   └── roles/              # Role definitions for multi-agent analysis
└── services/
    ├── llm_service.py      # LLM abstraction (supports minimax, anthropic, openai)
    ├── prediction_service.py
    ├── multi_agent_service.py
    └── worldmonitor_service.py
```

### Agent Pipeline Flow

1. **InfoCollectorAgent**: Collects event basic info, generates summary
2. **AnalyzerAgent**: Analyzes impact scope, duration, sentiment, risk, opportunities
3. **PredictorAgent**: Determines trend (UP/DOWN/SIDEWAYS/UNCERTAIN), calculates confidence

### Multi-Agent Analysis

The `MultiAgentAnalysisService` supports parallel role-based analysis with different stakeholder perspectives (government, corporation, public, media, investor). It performs:
- Per-role analysis using LLM
- Cross-analysis for conflicts and synergies
- Synthesis for overall predictions

### Configuration

- Primary config: `config.yaml` at project root
- Environment variables: See `.env.example` for required API keys
- LLM provider configured via `llm.provider` (minimax/anthropic/openai/mock)
- API keys read from environment: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `MINIMAX_API_KEY`

### Key Data Models

- **Event**: Input event with title, description, category, importance (1-5)
- **Prediction**: Output with trend, confidence (0-1), reasoning, time_horizon, factors
- **PredictResponse**: Enhanced response with visualization data (probability_distribution, scenario_analysis, etc.)

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| POST | /api/v1/predict | Submit event for prediction |
| GET | /api/v1/events | List events |
| GET | /api/v1/events/{id} | Get event details |
| POST | /api/v1/multi-agent/analyze | Multi-agent role analysis |

## Frontend Stack

- React 19 with TypeScript
- Vite for build tooling
- TailwindCSS for styling
- react-router-dom for routing
- recharts for data visualization
- react-globe.gl for 3D globe visualization
