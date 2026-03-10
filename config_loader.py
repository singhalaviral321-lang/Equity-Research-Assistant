"""
config_loader.py — Reads config.json and makes all values available.
Import this at the top of indicator_engine.py:

    from config_loader import CFG
    
Then use anywhere:
    CFG["indicator_params"]["rsi_period"]
    CFG["scoring_weights"]["technical"]
    CFG.stocks()   ← returns flat list of all tickers
"""

import json
import os

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_config(path: str = _CONFIG_PATH) -> dict:
    with open(path) as f:
        return json.load(f)

class Config(dict):
    """Dict subclass with helper methods."""

    def stocks(self) -> list[str]:
        """Return flat list of all configured tickers."""
        s = self.get("stocks", {})
        return (
            s.get("india_nse", []) +
            s.get("india_bse", []) +
            s.get("us_stocks", [])
        )

    def weights(self) -> dict:
        return self.get("scoring_weights", {
            "technical": 0.45, "volume": 0.25,
            "event": 0.15, "fundamental": 0.15
        })

    def thresholds(self) -> dict:
        return self.get("signal_thresholds", {
            "strong_buy": 72, "buy": 58, "neutral_low": 42, "sell": 28
        })

    def ind(self, key: str, default=None):
        """Shorthand: CFG.ind('rsi_period') → 14"""
        return self.get("indicator_params", {}).get(key, default)

    def rule(self, key: str, default: float = 0) -> float:
        """Shorthand: CFG.rule('macd_bullish_cross_bonus') → 15"""
        return float(self.get("scoring_rules", {}).get(key, default))

    def signal_for_score(self, score: float) -> str:
        t = self.thresholds()
        if score >= t["strong_buy"]:   return "STRONG BUY"
        if score >= t["buy"]:          return "BUY"
        if score >= t["neutral_low"]:  return "NEUTRAL"
        if score >= t["sell"]:         return "SELL"
        return "STRONG SELL"

# ── Singleton ─────────────────────────────────────────────────
try:
    CFG = Config(load_config())
    print(f"✅ Config loaded — {len(CFG.stocks())} stocks configured")
except FileNotFoundError:
    print("⚠  config.json not found — using defaults")
    CFG = Config({})
