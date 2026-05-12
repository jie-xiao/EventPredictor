# Prediction Model Upgrade Design

**Date:** 2026-05-12
**Status:** Approved
**Scope:** Phase 1 — Signal Calibration + Backtest Feedback Loop
**Deferred:** Phase 2 — Game-Theoretic Engine (博弈引擎)

## Problem Statement

The current system generates predictions via LLM narrative generation (InfoCollector → Analyzer → Predictor pipeline + Multi-Agent Role Analysis). There are three critical gaps:

1. **No feedback loop** — predictions are never validated against actual outcomes. The system never learns whether it was right.
2. **No structured signal calibration** — predictions rest entirely on unstructured text reasoning. No feature vectors, no historical baselines, no numerical anchor.
3. **Confidence is uncalibrated** — the "confidence score" is LLM self-estimated, known to be poorly calibrated in all LLM research.

### Distinction from Phase 2 (Game Engine)

Phase 1 addresses the data and validation foundation. Phase 2 (deferred) will add strategic interaction modeling (Nash/Stackelberg equilibria, payoff matrices, signaling games). The two phases are independent — Phase 1 can ship and prove value before Phase 2 begins.

## Design Philosophy

**Backend complex, frontend simple.** Feature extraction, backtesting, calibration, and outcome tracking all run silently on the backend. The user sees only high-density, actionable information:

- What happened (event)
- What will likely happen next (trend + confidence)
- Has the system been reliable (one accuracy number)

Complexity (Brier Score curves, calibration plots, backtest run history) lives behind an optional settings panel. The main UI embeds predictions directly into the existing event feed — no new pages, no navigation hops.

## Architecture

### Data Flow

```
Data Sources          Feature Extraction         Analysis              Feedback
─────────────        ──────────────────        ──────────            ──────────
RSS/News ──────┐                                   
Polymarket ────┤     Feature Extractor       Agent Pipeline          Outcome Tracker
GDELT (opt) ───┼───► (NLP + structured) ───► + Monte Carlo ────────► (auto + manual)
ACLED (opt) ───┘     → FeatureVector         + Bayesian               ↓
                                               + Causal            Calibration
                                                    ↓              (Platt/Isotonic)
                                              PredictionRecord       ↓
                                                    ↓             Updated Model
                                              EventCard UI         Confidence
```

### Feature Vector Schema

Every event is encoded into a structured vector before reaching any analysis component:

```
EventFeature:
  # Identity
  event_id, timestamp, source[]

  # NLP extraction
  event_type (CAMEO or custom), entities[], sentiment (-1..1),
  severity (0..1), urgency (0..1)

  # Structured indicators (nullable — populated when source available)
  goldstein_score (-10..10, from GDELT), casualty_count (from ACLED),
  market_prob (from Polymarket), market_volume

  # Relational
  parent_event, related_events[], geo_scope

  # Temporal
  signal_velocity (rate of change), novelty_score (vs historical)
```

### Two-Track Feedback

| | Offline Backtesting | Online Tracking |
|---|---|---|
| **Data** | Historical events (2020-2025) with known outcomes | Live predictions awaiting resolution |
| **Trigger** | Manual + CI on model change | Automatic (daily/weekly cron) |
| **Output** | Brier Score, AUC, Calibration Curve, Direction Accuracy | Update prediction status: pending → correct/incorrect |

### Outcome Resolution Sources

1. **Polymarket settlement** (automatic, ~60-70% coverage) — markets resolve with clear binary outcomes
2. **News condition matching** (semi-automatic) — keyword/entity matching against follow-up news
3. **Manual annotation** (fallback) — admin UI for human judgment on complex geopolitical events

### Calibration

After sufficient predictions are resolved, apply Platt scaling or isotonic regression to correct the raw confidence scores. This runs server-side; the user sees only "校准: 良好" or similar in the status bar.

## Backend Changes

### New Files

| File | Purpose |
|---|---|
| `app/services/feature_extractor.py` | NLP pipeline + feature vector construction |
| `app/services/gdelt_service.py` | GDELT 2.0 API client (optional data source) |
| `app/services/acled_service.py` | ACLED API client (optional data source) |
| `app/services/backtest_service.py` | Batch backtesting engine |
| `app/services/calibration_service.py` | Probability calibrator (Platt/Isotonic) |
| `app/services/outcome_tracker.py` | Periodic outcome resolution task |
| `app/api/routes/backtest.py` | Backtest run + results API |
| `app/api/routes/calibration.py` | Calibration metrics API |

### Modified Files

| File | Change |
|---|---|
| `app/services/data_service.py` | Add feature vector storage and query |
| `app/db/models.py` | Add EventFeature, PredictionRecord, BacktestRun tables |
| `app/main.py` | Register new routers |
| `config.yaml` | Add GDELT/ACLED keys, backtest config section |

## Frontend Changes

### Principle: Embed, Don't Add

Prediction display is merged into existing components. No new pages for the main flow.

### Modified Components

| Component | Change |
|---|---|
| `EventCard` (EventList.tsx or similar) | Embed trend badge + confidence ring + multi-model consensus inline |
| `FloatingToolbar` | Simplify to one-line status bar: Live indicator, tracked prediction count, 30-day directional accuracy, calibration rating |
| `Home.tsx` | Event feed becomes prediction feed |

### New Component (Hidden)

| Component | Where |
|---|---|
| `CalibrationPanel` | Settings page or `/calibration` route. Shows Brier Score curve, calibration plot, backtest history. Not visible in normal user flow. |

## Implementation Steps

| Step | What | Days |
|---|---|---|
| 1. Feature Extractor | NLP pipeline, FeatureVector model, integration with existing RSS/Polymarket flow | 3-4 |
| 2. GDELT + ACLED | Optional data source clients, pluggable into feature extractor | 2-3 |
| 3. Backtest Engine | Batch runner, metric computation (Brier/AUC/DirAcc), historical dataset preparation | 3-4 |
| 4. Outcome Tracker | Periodic resolution task, auto + manual resolution pipeline | 2-3 |
| 5. Calibration Service | Platt scaling, calibration curve computation | 1-2 |
| 6. Frontend Integration | EventCard embedding, simplified status bar, optional calibration panel | 3-4 |
| **Total** | | **14-20 days** |

## Deferred: Phase 2 — Game-Theoretic Engine

Key design decisions already made:

- **Strategy computation ≠ narrative generation.** The game engine computes equilibria algorithmically (Nash, Stackelberg, Bayesian games). LLM translates results into human-readable scenarios and injects them into role prompts.
- Requires: structured world state machine, payoff matrix per actor, equilibrium solver
- Depends on Phase 1 feature vectors as input

## Spec Self-Review

- No TBDs or placeholders
- Backend scope (8 new files, 3 modified) matches frontend principle (embed, don't add)
- GDELT/ACLED explicitly marked as optional/pluggable
- Outcome resolution has three-tier coverage (auto → semi-auto → manual)
- User-facing complexity is gated behind settings
