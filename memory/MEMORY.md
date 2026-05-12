# EventPredictor Project Memory

## Architecture
- **Backend:** Python/FastAPI, SQLite+SQLAlchemy async, JWT auth
- **Frontend:** React/TypeScript + Vite, Three.js globe visualization
- **ORM Models:** User, UserSession, UserPreferences, AnalysisHistory, Favorite, SharedReport, Workspace, WorkspaceMember, Comment, Notification, EventFeature, PredictionRecord, BacktestRun

## Key Modules
- `app/api/routes/` — REST endpoints (predict, events, auth, users, debate, multi-agent, SSE, notifications, backtest, calibration, etc.)
- `app/services/` — Business logic (prediction, feature extraction, calibration, outcome tracking, backtesting, knowledge graph, etc.)
- `app/agents/` — Multi-agent analysis pipeline (specialized agents, reaction chains, debate)
- `app/db/` — Database models, engine, session management

## Real-time Features (P2.3)
- SSE endpoint: `/api/v1/stream/events` with token auth (query param support)
- `useSSE` hook with exponential backoff reconnection
- Notification system with CRUD endpoints, user preferences
- NotificationCenter component with bell icon in FloatingToolbar

## Prediction Model Upgrade (P2.4)
- FeatureExtractor: NLP pipeline for structured feature vectors
- BacktestService: Brier score, directional accuracy, AUC, Sharpe ratio
- CalibrationService: Platt scaling, calibration rating
- OutcomeTracker: periodic auto-resolution of pending predictions
- Frontend: trend badges + confidence rings in event cards, calibration status bar
