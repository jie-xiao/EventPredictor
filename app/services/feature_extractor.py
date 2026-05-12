# app/services/feature_extractor.py
"""NLP feature extraction pipeline. Converts raw events into structured FeatureVectors."""
import re
import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

# ── Lightweight keyword-based extraction (no heavy NLP deps) ──

EVENT_TYPE_PATTERNS = [
    ("conflict_armed", ["military", "strike", "invasion", "troop", "missile", "war", "attack", "combat"]),
    ("conflict_diplomatic", ["sanction", "tariff", "embargo", "summit", "negotiation", "treaty", "diplomat"]),
    ("economic_policy", ["interest rate", "inflation", "fiscal", "monetary", "stimulus", "tax", "budget"]),
    ("economic_market", ["stock", "market crash", "rally", "bond", "currency", "exchange rate"]),
    ("disaster_natural", ["earthquake", "flood", "hurricane", "tsunami", "wildfire", "volcano"]),
    ("disaster_health", ["outbreak", "pandemic", "epidemic", "virus", "vaccine"]),
    ("political_election", ["election", "vote", "president", "parliament", "prime minister", "poll"]),
    ("political_protest", ["protest", "demonstration", "riot", "unrest", "coup"]),
    ("tech_breakthrough", ["AI", "artificial intelligence", "quantum", "breakthrough", "semiconductor"]),
    ("cyber_incident", ["cyber", "hack", "breach", "ransomware", "data leak"]),
]

ENTITY_PATTERNS = [
    ("USA", ["United States", "US", "America", "Washington", "White House", "Pentagon"]),
    ("China", ["China", "Chinese", "Beijing", "CCP", "PLA"]),
    ("Russia", ["Russia", "Russian", "Moscow", "Kremlin"]),
    ("EU", ["EU", "European Union", "Brussels"]),
    ("NATO", ["NATO"]),
    ("UN", ["UN", "United Nations"]),
    ("Iran", ["Iran", "Iranian", "Tehran"]),
    ("NorthKorea", ["North Korea", "DPRK", "Pyongyang"]),
    ("India", ["India", "Indian", "New Delhi"]),
    ("Japan", ["Japan", "Japanese", "Tokyo"]),
]

SENTIMENT_WORDS = {
    "negative": -1.0,
    "crisis": -0.9, "threat": -0.8, "conflict": -0.8, "attack": -0.9,
    "sanction": -0.6, "crash": -0.9, "collapse": -0.9, "tension": -0.7,
    "warning": -0.5, "risk": -0.5, "concern": -0.4, "fear": -0.7,
    "positive": 1.0,
    "agreement": 0.8, "peace": 0.9, "growth": 0.7, "breakthrough": 0.8,
    "cooperation": 0.7, "progress": 0.6, "recovery": 0.6, "opportunity": 0.5,
}


class FeatureExtractor:
    def __init__(self):
        self._seen_hashes: set[str] = set()
        self._max_seen = 10000

    async def extract(
        self,
        event: Dict[str, Any],
        polymarket_data: Optional[Dict] = None,
        gdelt_data: Optional[Dict] = None,
        acled_data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        title = event.get("title", "")
        description = event.get("description", "")
        text = f"{title} {description}".lower()
        timestamp_str = event.get("timestamp", datetime.now(timezone.utc).isoformat())

        # ── NLP extraction ──
        event_type = self._classify_event_type(text)
        entities = self._extract_entities(title, description)
        sentiment = self._compute_sentiment(text)
        severity = event.get("severity", 3) / 5.0  # Normalize 1-5 -> 0-1
        urgency = self._compute_urgency(text, event.get("severity", 3))

        # ── Structured indicators (nullable) ──
        goldstein = gdelt_data.get("goldstein_score") if gdelt_data else None
        casualties = acled_data.get("casualty_count") if acled_data else None
        market_prob = polymarket_data.get("probability") if polymarket_data else None
        market_vol = polymarket_data.get("volume") if polymarket_data else None

        # ── Relational ──
        geo_scope = self._classify_geo_scope(text, event)

        # ── Temporal ──
        content_hash = hashlib.md5(text.encode()).hexdigest()
        novelty = 0.0 if content_hash in self._seen_hashes else 1.0
        self._seen_hashes.add(content_hash)
        if len(self._seen_hashes) > self._max_seen:
            self._seen_hashes.clear()

        velocity = self._compute_velocity(event)

        features = {
            "event_id": event.get("id", ""),
            "timestamp": timestamp_str,
            "sources": event.get("source", "unknown").split(","),
            "event_type": event_type,
            "entities": entities,
            "sentiment": sentiment,
            "severity": severity,
            "urgency": urgency,
            "goldstein_score": goldstein,
            "casualty_count": casualties,
            "market_prob": market_prob,
            "market_volume": market_vol,
            "parent_event": event.get("parent_event"),
            "related_events": event.get("related_events", []),
            "geo_scope": geo_scope,
            "signal_velocity": velocity,
            "novelty_score": novelty,
            "raw_json": event,
        }
        return features

    def _classify_event_type(self, text: str) -> Optional[str]:
        best_type = None
        best_score = 0
        for etype, keywords in EVENT_TYPE_PATTERNS:
            score = sum(1 for kw in keywords if kw in text)
            if score > best_score:
                best_score = score
                best_type = etype
        return best_type if best_score > 0 else "other"

    def _extract_entities(self, title: str, description: str) -> List[Dict[str, str]]:
        combined = f"{title} {description}"
        entities = []
        seen_names = set()
        for name, patterns in ENTITY_PATTERNS:
            for pat in patterns:
                if pat.lower() in combined.lower() and name not in seen_names:
                    entities.append({"name": name, "role": "actor", "country": name, "type": "nation"})
                    seen_names.add(name)
                    break
        return entities

    def _compute_sentiment(self, text: str) -> float:
        scores = []
        for word, score in SENTIMENT_WORDS.items():
            if word in text:
                scores.append(score)
        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 3)

    def _compute_urgency(self, text: str, severity: int) -> float:
        urgent_words = ["immediate", "urgent", "emergency", "breaking", "crisis", "now"]
        matches = sum(1 for w in urgent_words if w in text)
        base = severity / 5.0
        boost = min(matches * 0.15, 0.5)
        return round(min(base + boost, 1.0), 3)

    def _classify_geo_scope(self, text: str, event: Dict) -> str:
        global_keywords = ["world", "global", "international", "UN", "NATO", "G20", "G7"]
        if any(kw.lower() in text for kw in global_keywords):
            return "global"
        entities = self._extract_entities(event.get("title", ""), event.get("description", ""))
        if len(entities) >= 3:
            return "regional"
        return "national"

    def _compute_velocity(self, event: Dict) -> float:
        return 0.5  # Default; enhanced when used with time-series context


# Global singleton
feature_extractor = FeatureExtractor()
