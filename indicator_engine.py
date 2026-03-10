"""
╔══════════════════════════════════════════════════════════════╗
║         EQUITY RESEARCH ASSISTANT - INDICATOR ENGINE         ║
║         Drop into n8n Code Node or run standalone            ║
╚══════════════════════════════════════════════════════════════╝

Install deps: pip install yfinance pandas numpy ta requests python-dotenv

Usage:
  python indicator_engine.py --stocks RELIANCE.NS,TCS.NS,INFY.NS
  python indicator_engine.py --file stocks.txt
  python indicator_engine.py  (reads from stocks.txt by default)
"""

import os
import json
import warnings
import argparse
import sys
from datetime import datetime, timedelta
from typing import Any

warnings.filterwarnings("ignore")

try:
    from config_loader import CFG
except Exception:
    CFG = {}

# ─── Try importing optional deps gracefully ───────────────────
try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False
    print("⚠  Missing deps. Run: pip install yfinance pandas numpy ta requests")
    sys.exit(1)

try:
    import ta
    HAS_TA = True
except ImportError:
    HAS_TA = False


# ══════════════════════════════════════════════════════════════
#  SECTION 1 — DATA FETCHER
# ══════════════════════════════════════════════════════════════

def fetch_ohlcv(ticker: str, period: str = None, interval: str = None) -> pd.DataFrame:
    """Fetch OHLCV data from Yahoo Finance."""
    if period is None:
        period = CFG.get("data", {}).get("history_period", "6mo") if hasattr(CFG, "get") else "6mo"
    if interval is None:
        interval = CFG.get("data", {}).get("history_interval", "1d") if hasattr(CFG, "get") else "1d"
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        if df.empty:
            print(f"  ⚠  No data for {ticker}")
            return pd.DataFrame()
        df.index = pd.to_datetime(df.index)
        df.columns = [c.lower() for c in df.columns]
        return df
    except Exception as e:
        print(f"  ✗  Error fetching {ticker}: {e}")
        return pd.DataFrame()


def fetch_stock_info(ticker: str) -> dict:
    """Fetch company metadata & fundamentals."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "name":          info.get("longName", ticker),
            "sector":        info.get("sector", "Unknown"),
            "industry":      info.get("industry", "Unknown"),
            "market_cap":    info.get("marketCap", 0),
            "pe_ratio":      info.get("trailingPE", None),
            "pb_ratio":      info.get("priceToBook", None),
            "dividend_yield":info.get("dividendYield", 0),
            "52w_high":      info.get("fiftyTwoWeekHigh", None),
            "52w_low":       info.get("fiftyTwoWeekLow", None),
            "analyst_target":info.get("targetMeanPrice", None),
            "recommendation":info.get("recommendationKey", "none"),
            "earnings_date": _safe_earnings_date(stock),
        }
    except Exception:
        return {"name": ticker, "sector": "Unknown", "industry": "Unknown"}


def _safe_earnings_date(stock) -> str | None:
    """Extract next earnings date safely."""
    try:
        cal = stock.calendar
        if cal is not None and not cal.empty:
            dates = cal.get("Earnings Date", [])
            if len(dates):
                return str(dates[0].date())
    except Exception:
        pass
    return None


# ══════════════════════════════════════════════════════════════
#  SECTION 2 — INDICATOR CALCULATOR
# ══════════════════════════════════════════════════════════════

def compute_indicators(df: pd.DataFrame) -> dict:
    """
    Compute 30+ technical indicators.
    Returns a flat dict of named signals.
    """
    if df.empty or len(df) < 30:
        return {}

    c  = df["close"]
    h  = df["high"]
    l  = df["low"]
    v  = df["volume"]
    o  = df["open"]

    ind = {}

    # ── Price Basics ─────────────────────────────────────────
    ind["price"]         = round(float(c.iloc[-1]), 2)
    ind["price_1d_chg"]  = round(float((c.iloc[-1] - c.iloc[-2]) / c.iloc[-2] * 100), 2)
    ind["price_1w_chg"]  = round(float((c.iloc[-1] - c.iloc[-6]) / c.iloc[-6] * 100), 2)
    ind["price_1m_chg"]  = round(float((c.iloc[-1] - c.iloc[-22]) / c.iloc[-22] * 100), 2)

    # ── Moving Averages ──────────────────────────────────────
    ind["sma_20"]  = round(float(c.rolling(20).mean().iloc[-1]), 2)
    ind["sma_50"]  = round(float(c.rolling(50).mean().iloc[-1]), 2)
    ind["sma_200"] = round(float(c.rolling(200).mean().iloc[-1]), 2) if len(df) >= 200 else None
    ind["ema_9"]   = round(float(c.ewm(span=9).mean().iloc[-1]), 2)
    ind["ema_21"]  = round(float(c.ewm(span=21).mean().iloc[-1]), 2)
    ind["ema_50"]  = round(float(c.ewm(span=50).mean().iloc[-1]), 2)

    # ── Golden / Death Cross ─────────────────────────────────
    ind["golden_cross"]  = bool(ind["sma_50"] > ind["sma_200"]) if ind["sma_200"] else False
    ind["price_vs_sma50"]  = round((ind["price"] - ind["sma_50"]) / ind["sma_50"] * 100, 2)
    ind["price_vs_sma200"] = round((ind["price"] - ind["sma_200"]) / ind["sma_200"] * 100, 2) if ind["sma_200"] else None

    # ── RSI ──────────────────────────────────────────────────
    delta = c.diff()
    rsi_period = CFG.ind("rsi_period", 14) if hasattr(CFG, "ind") else 14
    gain  = delta.clip(lower=0).rolling(rsi_period).mean()
    loss  = (-delta.clip(upper=0)).rolling(rsi_period).mean()
    rs    = gain / loss
    rsi   = 100 - (100 / (1 + rs))
    ind["rsi_14"]      = round(float(rsi.iloc[-1]), 1)
    ind["rsi_signal"]  = _rsi_signal(ind["rsi_14"])

    # ── MACD ─────────────────────────────────────────────────
    macd_fast = CFG.ind("macd_fast", 12) if hasattr(CFG, "ind") else 12
    macd_slow = CFG.ind("macd_slow", 26) if hasattr(CFG, "ind") else 26
    macd_sig  = CFG.ind("macd_signal", 9) if hasattr(CFG, "ind") else 9
    ema12  = c.ewm(span=macd_fast).mean()
    ema26  = c.ewm(span=macd_slow).mean()
    macd   = ema12 - ema26
    signal = macd.ewm(span=macd_sig).mean()
    hist   = macd - signal
    ind["macd"]           = round(float(macd.iloc[-1]), 4)
    ind["macd_signal"]    = round(float(signal.iloc[-1]), 4)
    ind["macd_histogram"] = round(float(hist.iloc[-1]), 4)
    ind["macd_crossover"] = _macd_crossover(hist)

    # ── Bollinger Bands ──────────────────────────────────────
    bb_period = CFG.ind("bb_period", 20) if hasattr(CFG, "ind") else 20
    bb_std_dev = CFG.ind("bb_std_dev", 2) if hasattr(CFG, "ind") else 2
    sma20  = c.rolling(bb_period).mean()
    std20  = c.rolling(bb_period).std()
    bb_up  = sma20 + bb_std_dev * std20
    bb_lo  = sma20 - bb_std_dev * std20
    ind["bb_upper"]    = round(float(bb_up.iloc[-1]), 2)
    ind["bb_lower"]    = round(float(bb_lo.iloc[-1]), 2)
    ind["bb_width"]    = round(float(((bb_up - bb_lo) / sma20).iloc[-1] * 100), 2)
    ind["bb_position"] = round(float((c.iloc[-1] - bb_lo.iloc[-1]) / (bb_up.iloc[-1] - bb_lo.iloc[-1]) * 100), 1)
    ind["bb_squeeze"]  = bool(ind["bb_width"] < ind["bb_width"] * 0.8)  # narrow band = squeeze

    # ── ATR (Volatility) ─────────────────────────────────────
    atr_period = CFG.ind("atr_period", 14) if hasattr(CFG, "ind") else 14
    tr  = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(atr_period).mean()
    ind["atr_14"]       = round(float(atr.iloc[-1]), 2)
    ind["atr_pct"]      = round(float(atr.iloc[-1] / c.iloc[-1] * 100), 2)

    # ── Stochastic Oscillator ────────────────────────────────
    stoch_period = CFG.ind("stoch_period", 14) if hasattr(CFG, "ind") else 14
    stoch_smooth = CFG.ind("stoch_smooth", 3) if hasattr(CFG, "ind") else 3
    low14  = l.rolling(stoch_period).min()
    high14 = h.rolling(stoch_period).max()
    stoch_k = (c - low14) / (high14 - low14) * 100
    stoch_d = stoch_k.rolling(stoch_smooth).mean()
    ind["stoch_k"]      = round(float(stoch_k.iloc[-1]), 1)
    ind["stoch_d"]      = round(float(stoch_d.iloc[-1]), 1)
    ind["stoch_signal"] = _stoch_signal(ind["stoch_k"], ind["stoch_d"])

    # ── Williams %R ──────────────────────────────────────────
    wr = (high14 - c) / (high14 - low14) * -100
    ind["williams_r"]   = round(float(wr.iloc[-1]), 1)

    # ── CCI ──────────────────────────────────────────────────
    cci_period = CFG.ind("cci_period", 20) if hasattr(CFG, "ind") else 20
    tp  = (h + l + c) / 3
    cci = (tp - tp.rolling(cci_period).mean()) / (0.015 * tp.rolling(cci_period).std())
    ind["cci_20"]       = round(float(cci.iloc[-1]), 1)

    # ── ADX (Trend Strength) ─────────────────────────────────
    adx_period = CFG.ind("adx_period", 14) if hasattr(CFG, "ind") else 14
    ind["adx"]         = round(float(_compute_adx(h, l, c, period=adx_period)), 1)
    ind["trend_strength"] = _adx_label(ind["adx"])

    # ── OBV (Volume) ─────────────────────────────────────────
    obv_direction = np.sign(c.diff())
    obv = (v * obv_direction).cumsum()
    ind["obv"]          = float(obv.iloc[-1])
    ind["obv_trend"]    = "rising" if obv.iloc[-1] > obv.iloc[-5] else "falling"

    # ── Volume Spike ─────────────────────────────────────────
    vol_avg20 = v.rolling(20).mean()
    ind["volume_ratio"]  = round(float(v.iloc[-1] / vol_avg20.iloc[-1]), 2)
    vol_spike_ratio = CFG.ind("volume_spike_ratio", 1.5) if hasattr(CFG, "ind") else 1.5
    ind["volume_spike"]  = bool(ind["volume_ratio"] > vol_spike_ratio)

    # ── Money Flow Index ─────────────────────────────────────
    mfi_period = CFG.ind("mfi_period", 14) if hasattr(CFG, "ind") else 14
    tp_mfi   = (h + l + c) / 3
    mf       = tp_mfi * v
    pos_flow = mf.where(tp_mfi > tp_mfi.shift(1), 0).rolling(mfi_period).sum()
    neg_flow = mf.where(tp_mfi <= tp_mfi.shift(1), 0).rolling(mfi_period).sum()
    mfi      = 100 - (100 / (1 + pos_flow / neg_flow.replace(0, np.nan)))
    ind["mfi_14"]       = round(float(mfi.iloc[-1]), 1)

    # ── ROC (Rate of Change) ─────────────────────────────────
    ind["roc_10"]       = round(float((c.iloc[-1] - c.iloc[-11]) / c.iloc[-11] * 100), 2)
    ind["roc_20"]       = round(float((c.iloc[-1] - c.iloc[-21]) / c.iloc[-21] * 100), 2)

    # ── Parabolic SAR ────────────────────────────────────────
    ind["sar_signal"]   = _compute_sar_signal(h, l, c)

    # ── SuperTrend ───────────────────────────────────────────
    st_period = CFG.ind("supertrend_period", 10) if hasattr(CFG, "ind") else 10
    st_mult   = CFG.ind("supertrend_mult", 3.0) if hasattr(CFG, "ind") else 3.0
    ind["supertrend"]   = _compute_supertrend(h, l, c, atr, period=st_period, multiplier=st_mult)

    # ── Pivot Points (Daily) ─────────────────────────────────
    prev_h = float(h.iloc[-2])
    prev_l = float(l.iloc[-2])
    prev_c = float(c.iloc[-2])
    pivot  = (prev_h + prev_l + prev_c) / 3
    ind["pivot"]   = round(pivot, 2)
    ind["r1"]      = round(2 * pivot - prev_l, 2)
    ind["r2"]      = round(pivot + (prev_h - prev_l), 2)
    ind["s1"]      = round(2 * pivot - prev_h, 2)
    ind["s2"]      = round(pivot - (prev_h - prev_l), 2)

    # ── 52W High/Low Proximity ───────────────────────────────
    high_52w = float(c.rolling(252).max().iloc[-1]) if len(df) >= 252 else float(c.max())
    low_52w  = float(c.rolling(252).min().iloc[-1]) if len(df) >= 252 else float(c.min())
    ind["pct_from_52w_high"] = round((c.iloc[-1] - high_52w) / high_52w * 100, 2)
    ind["pct_from_52w_low"]  = round((c.iloc[-1] - low_52w) / low_52w * 100, 2)

    # ── Chaikin Money Flow ───────────────────────────────────
    cmf_period = CFG.ind("cmf_period", 20) if hasattr(CFG, "ind") else 20
    clv = ((c - l) - (h - c)) / (h - l).replace(0, np.nan)
    cmf = (clv * v).rolling(cmf_period).sum() / v.rolling(cmf_period).sum()
    ind["cmf_20"]       = round(float(cmf.iloc[-1]), 3)

    return ind


# ── Helper computations ───────────────────────────────────────

def _rsi_signal(rsi: float) -> str:
    if rsi >= 70:   return "overbought"
    if rsi >= 55:   return "bullish"
    if rsi >= 45:   return "neutral"
    if rsi >= 30:   return "bearish"
    return "oversold"

def _stoch_signal(k: float, d: float) -> str:
    if k > 80:      return "overbought"
    if k < 20:      return "oversold"
    if k > d:       return "bullish_cross"
    return "bearish_cross"

def _macd_crossover(hist: pd.Series) -> str:
    if hist.iloc[-1] > 0 and hist.iloc[-2] <= 0: return "bullish_crossover"
    if hist.iloc[-1] < 0 and hist.iloc[-2] >= 0: return "bearish_crossover"
    if hist.iloc[-1] > hist.iloc[-2]:            return "strengthening"
    return "weakening"

def _adx_label(adx: float) -> str:
    if adx >= 40:   return "very_strong"
    if adx >= 25:   return "strong"
    if adx >= 20:   return "moderate"
    return "weak"

def _compute_adx(h: pd.Series, l: pd.Series, c: pd.Series, period: int = 14) -> float:
    """Compute ADX value."""
    try:
        tr   = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
        dm_p = h.diff().clip(lower=0)
        dm_n = (-l.diff()).clip(lower=0)
        dm_p = dm_p.where(dm_p > dm_n, 0)
        dm_n = dm_n.where(dm_n > dm_p.shift(), 0)
        tr_s = tr.rolling(period).sum()
        di_p = 100 * dm_p.rolling(period).sum() / tr_s
        di_n = 100 * dm_n.rolling(period).sum() / tr_s
        dx   = 100 * (di_p - di_n).abs() / (di_p + di_n)
        adx  = dx.rolling(period).mean()
        return float(adx.iloc[-1])
    except Exception:
        return 0.0

def _compute_sar_signal(h, l, c) -> str:
    """Simplified SAR signal (above/below price)."""
    try:
        # Simplified: use recent low as SAR reference
        sar_ref = float(l.rolling(5).min().iloc[-2])
        return "bullish" if float(c.iloc[-1]) > sar_ref else "bearish"
    except Exception:
        return "neutral"

def _compute_supertrend(h, l, c, atr, period=10, multiplier=3.0) -> str:
    """Simplified SuperTrend signal."""
    try:
        hl2    = (h + l) / 2
        upper  = hl2 + multiplier * atr
        lower  = hl2 - multiplier * atr
        # Use last few bars to determine direction
        above  = float(c.iloc[-1]) > float(lower.iloc[-1])
        return "bullish" if above else "bearish"
    except Exception:
        return "neutral"


# ══════════════════════════════════════════════════════════════
#  SECTION 3 — SCORING ENGINE
# ══════════════════════════════════════════════════════════════

def score_stock(ind: dict, info: dict) -> dict:
    """
    Produce a composite score (0–100) across 4 dimensions.
    Returns scores + final signal + key reasons.
    """
    tech_score   = _technical_score(ind)
    vol_score    = _volume_score(ind)
    event_score  = _event_score(info)
    fundam_score = _fundamental_score(info)

    # Weighted composite
    weights = CFG.weights() if hasattr(CFG, "weights") else {"technical": 0.45, "volume": 0.25, "event": 0.15, "fundamental": 0.15}
    composite = (
        tech_score   * weights.get("technical", 0.45) +
        vol_score    * weights.get("volume", 0.25)    +
        event_score  * weights.get("event", 0.15)     +
        fundam_score * weights.get("fundamental", 0.15)
    )

    if hasattr(CFG, "signal_for_score"):
        signal = CFG.signal_for_score(composite)
    else:
        signal = "STRONG BUY" if composite >= 72 else \
                 "BUY"        if composite >= 58 else \
                 "NEUTRAL"    if composite >= 42 else \
                 "SELL"       if composite >= 28 else \
                 "STRONG SELL"

    return {
        "composite_score": round(composite, 1),
        "technical_score": round(tech_score, 1),
        "volume_score":    round(vol_score, 1),
        "event_score":     round(event_score, 1),
        "fundamental_score": round(fundam_score, 1),
        "signal":          signal,
        "reasons":         _build_reasons(ind, info, composite),
        "risks":           _build_risks(ind, info),
    }


def _technical_score(ind: dict) -> float:
    score = 50.0

    # RSI
    rsi = ind.get("rsi_14", 50)
    if 50 < rsi < 65:   score += CFG.rule("rsi_bullish_zone_bonus", 12)
    elif rsi >= 65:      score += CFG.rule("rsi_overbought_penalty", -5)
    elif rsi < 35:       score += CFG.rule("rsi_oversold_penalty", -15)
    elif rsi < 45:       score += -7

    # MACD
    mc = ind.get("macd_crossover", "")
    if mc == "bullish_crossover":  score += CFG.rule("macd_bullish_cross_bonus", 15)
    elif mc == "strengthening":    score += CFG.rule("macd_strengthen_bonus", 7)
    elif mc == "bearish_crossover":score += CFG.rule("macd_bearish_cross_penalty", -15)
    elif mc == "weakening":        score += CFG.rule("macd_weaken_penalty", -7)

    # Price vs MAs
    p50  = ind.get("price_vs_sma50", 0) or 0
    p200 = ind.get("price_vs_sma200", 0) or 0
    if p50 > 0:    score += CFG.rule("price_above_sma50_bonus", 8)
    if p200 > 0:   score += CFG.rule("price_above_sma200_bonus", 8)
    if p50 < 0:    score += CFG.rule("price_below_sma50_penalty", -10)
    if p200 < 0:   score -= 10

    # Golden Cross
    if ind.get("golden_cross"):    score += CFG.rule("golden_cross_bonus", 5)

    # ADX
    ts = ind.get("trend_strength", "weak")
    if ts in ("strong", "very_strong"): score += CFG.rule("adx_strong_bonus", 5)

    # SuperTrend + SAR
    if ind.get("supertrend") == "bullish": score += CFG.rule("supertrend_bullish_bonus", 6)
    if ind.get("sar_signal") == "bullish": score += CFG.rule("sar_bullish_bonus", 4)

    # BB Position (prefer middle-to-upper range, not extreme)
    bp = ind.get("bb_position", 50)
    if 40 < bp < 80:   score += 5
    elif bp >= 95:      score -= 5   # extreme overbought
    elif bp <= 10:      score -= 5

    # 52W High proximity
    p52h = ind.get("pct_from_52w_high", -50)
    if p52h >= -5:     score += CFG.rule("near_52w_high_bonus", 8)
    elif p52h <= -30:  score += CFG.rule("far_from_52w_high_penalty", -8)

    return max(0, min(100, score))


def _volume_score(ind: dict) -> float:
    score = 50.0

    # Volume spike on up day
    vr   = ind.get("volume_ratio", 1)
    chg  = ind.get("price_1d_chg", 0)
    if vr > 1.5 and chg > 0:  score += CFG.rule("volume_spike_up_bonus", 20)
    elif vr > 1.5 and chg < 0: score += CFG.rule("volume_spike_down_penalty", -20)
    elif vr > 1.2:             score += 8

    # OBV trend
    if ind.get("obv_trend") == "rising":  score += CFG.rule("obv_rising_bonus", 12)
    else:                                  score += CFG.rule("obv_falling_penalty", -8)

    # MFI
    mfi = ind.get("mfi_14", 50)
    if 50 < mfi < 75:   score += CFG.rule("mfi_bullish_bonus", 10)
    elif mfi >= 75:      score += CFG.rule("mfi_overbought_penalty", -5)
    elif mfi < 30:       score -= 12

    # CMF
    cmf = ind.get("cmf_20", 0)
    if cmf > 0.1:    score += CFG.rule("cmf_positive_bonus", 10)
    elif cmf < -0.1: score += CFG.rule("cmf_negative_penalty", -10)

    return max(0, min(100, score))


def _event_score(info: dict) -> float:
    score = 50.0
    rec = info.get("recommendation", "none")
    if rec in ("buy", "strongBuy"):    score += 20
    elif rec in ("sell", "strongSell"):score -= 20
    # Earnings proximity bonus (coming soon = volatile)
    ed = info.get("earnings_date")
    if ed:
        try:
            days = (datetime.strptime(ed, "%Y-%m-%d") - datetime.now()).days
            if 0 < days <= 7:   score -= 10   # event risk
            elif 7 < days <= 14: score += 5   # build-up
        except Exception:
            pass
    return max(0, min(100, score))


def _fundamental_score(info: dict) -> float:
    score = 50.0
    pe = info.get("pe_ratio")
    pb = info.get("pb_ratio")
    dy = info.get("dividend_yield", 0) or 0
    at = info.get("analyst_target")
    price = info.get("current_price", 0)

    if pe and 10 < pe < 25:   score += 15
    elif pe and pe > 50:       score -= 10
    elif pe and pe < 0:        score -= 15

    if pb and 0 < pb < 3:     score += 10

    if dy > 0.02:              score += 8   # >2% yield

    if at and price:
        upside = (at - price) / price * 100
        if upside > 15:        score += 15
        elif upside < -10:     score -= 10

    return max(0, min(100, score))


def _build_reasons(ind: dict, info: dict, score: float) -> list[str]:
    reasons = []
    if ind.get("rsi_signal") in ("bullish",):
        reasons.append(f"RSI at {ind.get('rsi_14')} — healthy momentum zone")
    if ind.get("macd_crossover") == "bullish_crossover":
        reasons.append("MACD bullish crossover — trend turning up")
    if ind.get("macd_crossover") == "strengthening":
        reasons.append("MACD histogram expanding — momentum building")
    if ind.get("golden_cross"):
        reasons.append("50 DMA above 200 DMA — golden cross intact")
    if ind.get("volume_spike") and ind.get("price_1d_chg", 0) > 0:
        reasons.append(f"Volume {ind.get('volume_ratio')}x average — breakout conviction")
    if ind.get("obv_trend") == "rising":
        reasons.append("OBV rising — accumulation pattern")
    if ind.get("supertrend") == "bullish":
        reasons.append("SuperTrend bullish — trend following signal")
    p52h = ind.get("pct_from_52w_high", -100)
    if p52h >= -5:
        reasons.append(f"Within {abs(p52h):.1f}% of 52-week high — price strength")
    rec = info.get("recommendation", "")
    if rec in ("buy", "strongBuy"):
        reasons.append(f"Analyst consensus: {rec.upper()}")
    return reasons[:5]  # top 5


def _build_risks(ind: dict, info: dict) -> list[str]:
    risks = []
    rsi = ind.get("rsi_14", 50)
    if rsi > 70:
        risks.append(f"RSI overbought at {rsi} — pullback risk")
    if ind.get("macd_crossover") in ("bearish_crossover", "weakening"):
        risks.append("MACD weakening — momentum fading")
    if ind.get("price_vs_sma50", 0) < 0:
        risks.append("Price below 50 DMA — bearish structure")
    if ind.get("price_vs_sma200", 1) is not None and ind.get("price_vs_sma200", 1) < 0:
        risks.append("Price below 200 DMA — long-term downtrend")
    if ind.get("volume_spike") and ind.get("price_1d_chg", 0) < 0:
        risks.append("High volume on red day — distribution signal")
    ed = info.get("earnings_date")
    if ed:
        try:
            days = (datetime.strptime(ed, "%Y-%m-%d") - datetime.now()).days
            if 0 < days <= 7:
                risks.append(f"Earnings in {days} days — event risk")
        except Exception:
            pass
    return risks[:4]


# ══════════════════════════════════════════════════════════════
#  SECTION 4 — NEWS & EVENT FETCHER
# ══════════════════════════════════════════════════════════════

def fetch_news_sentiment(ticker: str, api_key: str | None = None) -> dict:
    """
    Fetch recent news headlines and compute a basic sentiment score.
    Uses Finnhub (free) if api_key provided, else Yahoo Finance news.
    """
    headlines = []
    sentiment = 0.0

    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        news  = stock.news or []
        for item in news[:10]:
            title = item.get("title", "")
            headlines.append(title)
            # Naive keyword sentiment
            sentiment += _keyword_sentiment(title)
        sentiment = sentiment / max(len(headlines), 1)
    except Exception:
        pass

    return {
        "headlines":  headlines[:5],
        "sentiment_score": round(sentiment, 2),
        "sentiment_label": "positive" if sentiment > 0.1 else "negative" if sentiment < -0.1 else "neutral",
    }


def _keyword_sentiment(text: str) -> float:
    """Simple keyword-based sentiment scoring."""
    text  = text.lower()
    pos   = ["surge", "rally", "beat", "record", "growth", "strong", "upgrade",
             "buy", "bullish", "profit", "gain", "rise", "high", "positive"]
    neg   = ["fall", "drop", "miss", "loss", "weak", "downgrade", "sell",
             "bearish", "decline", "crash", "concern", "risk", "negative", "cut"]
    score = sum(1 for w in pos if w in text) - sum(1 for w in neg if w in text)
    return float(max(-1, min(1, score)))


# ══════════════════════════════════════════════════════════════
#  SECTION 5 — MAIN ORCHESTRATOR
# ══════════════════════════════════════════════════════════════

def analyze_stock(ticker: str) -> dict:
    """Full analysis pipeline for one stock."""
    print(f"  → Analyzing {ticker}...")

    df   = fetch_ohlcv(ticker)
    if df.empty:
        return {"ticker": ticker, "error": "No data"}

    info = fetch_stock_info(ticker)
    info["current_price"] = float(df["close"].iloc[-1])

    ind  = compute_indicators(df)
    if not ind:
        return {"ticker": ticker, "error": "Insufficient data"}

    news = fetch_news_sentiment(ticker)
    scr  = score_stock(ind, info)

    return {
        "ticker":      ticker,
        "name":        info.get("name", ticker),
        "sector":      info.get("sector", "Unknown"),
        "price":       ind["price"],
        "change_1d":   ind["price_1d_chg"],
        "change_1w":   ind["price_1w_chg"],
        "change_1m":   ind["price_1m_chg"],
        "signal":      scr["signal"],
        "composite_score": scr["composite_score"],
        "scores": {
            "technical":   scr["technical_score"],
            "volume":      scr["volume_score"],
            "event":       scr["event_score"],
            "fundamental": scr["fundamental_score"],
        },
        "key_indicators": {
            "rsi":            ind.get("rsi_14"),
            "rsi_signal":     ind.get("rsi_signal"),
            "macd_crossover": ind.get("macd_crossover"),
            "adx":            ind.get("adx"),
            "trend_strength": ind.get("trend_strength"),
            "supertrend":     ind.get("supertrend"),
            "volume_ratio":   ind.get("volume_ratio"),
            "obv_trend":      ind.get("obv_trend"),
            "bb_position":    ind.get("bb_position"),
            "stoch_k":        ind.get("stoch_k"),
            "cmf":            ind.get("cmf_20"),
            "mfi":            ind.get("mfi_14"),
        },
        "price_levels": {
            "sma_50":  ind.get("sma_50"),
            "sma_200": ind.get("sma_200"),
            "ema_21":  ind.get("ema_21"),
            "bb_upper":ind.get("bb_upper"),
            "bb_lower":ind.get("bb_lower"),
            "pivot":   ind.get("pivot"),
            "r1": ind.get("r1"), "r2": ind.get("r2"),
            "s1": ind.get("s1"), "s2": ind.get("s2"),
            "pct_from_52w_high": ind.get("pct_from_52w_high"),
        },
        "fundamentals": {
            "pe":              info.get("pe_ratio"),
            "pb":              info.get("pb_ratio"),
            "dividend_yield":  info.get("dividend_yield"),
            "analyst_target":  info.get("analyst_target"),
            "recommendation":  info.get("recommendation"),
            "earnings_date":   info.get("earnings_date"),
            "market_cap":      info.get("market_cap"),
        },
        "news": news,
        "reasons": scr["reasons"],
        "risks":   scr["risks"],
        "analyzed_at": datetime.now().isoformat(),
    }


def run_daily_analysis(tickers: list[str] = None) -> dict:
    """Run analysis on a pool of stocks and generate a daily report."""
    if tickers is None:
        tickers = CFG.stocks() if hasattr(CFG, "stocks") else []
    
    if not tickers:
        print("⚠ No tickers provided or found in config.")
        return {}
    print(f"\n{'═'*60}")
    print(f"  EQUITY RESEARCH ASSISTANT — {datetime.now().strftime('%d %b %Y %H:%M')}")
    print(f"  Analyzing {len(tickers)} stocks...")
    print(f"{'═'*60}")

    results = []
    for t in tickers:
        r = analyze_stock(t.strip().upper())
        results.append(r)

    # Sort by composite score
    valid   = [r for r in results if "error" not in r]
    errored = [r for r in results if "error" in r]
    valid.sort(key=lambda x: x["composite_score"], reverse=True)

    # Categorize
    strong_buys  = [r for r in valid if r["signal"] in ("STRONG BUY",)]
    buys         = [r for r in valid if r["signal"] == "BUY"]
    neutrals     = [r for r in valid if r["signal"] == "NEUTRAL"]
    sells        = [r for r in valid if r["signal"] in ("SELL", "STRONG SELL")]

    top_count = CFG.get("output", {}).get("top_picks_count", 5) if hasattr(CFG, "get") else 5
    avoid_count = CFG.get("output", {}).get("avoid_count", 5) if hasattr(CFG, "get") else 5
    
    report = {
        "date":        datetime.now().strftime("%Y-%m-%d"),
        "time":        datetime.now().strftime("%H:%M"),
        "total_stocks": len(tickers),
        "summary": {
            "strong_buys": len(strong_buys),
            "buys":        len(buys),
            "neutrals":    len(neutrals),
            "sells":       len(sells),
            "errors":      len(errored),
        },
        "top_momentum":   valid[:top_count],
        "watchlist":      buys[:top_count],
        "avoid":          sells[:avoid_count],
        "all_results":    valid,
        "errors":         errored,
    }

    # Print console summary
    _print_report(report)
    return report


def _print_report(report: dict):
    def sig_emoji(s):
        return {"STRONG BUY":"🟢🟢","BUY":"🟢","NEUTRAL":"🟡","SELL":"🔴","STRONG SELL":"🔴🔴"}.get(s,"⚪")

    print(f"\n📊 DAILY SUMMARY")
    print(f"  🟢 Strong Buy: {report['summary']['strong_buys']}  "
          f"🟢 Buy: {report['summary']['buys']}  "
          f"🟡 Neutral: {report['summary']['neutrals']}  "
          f"🔴 Sell/Avoid: {report['summary']['sells']}")

    print(f"\n🚀 TOP MOMENTUM PICKS")
    for r in report["top_momentum"]:
        print(f"  {sig_emoji(r['signal'])} {r['ticker']:12s}  Score:{r['composite_score']:5.1f}  "
              f"RSI:{r['key_indicators']['rsi']:5.1f}  "
              f"1D:{r['change_1d']:+.2f}%  {r['signal']}")
        for reason in r["reasons"][:2]:
            print(f"     • {reason}")

    if report["avoid"]:
        print(f"\n⚠️  STOCKS TO AVOID / WATCH FOR SHORTS")
        for r in report["avoid"]:
            print(f"  🔴 {r['ticker']:12s}  Score:{r['composite_score']:5.1f}  "
                  f"RSI:{r['key_indicators']['rsi']:5.1f}  1D:{r['change_1d']:+.2f}%")
            for risk in r["risks"][:2]:
                print(f"     ⚡ {risk}")

    print(f"\n{'═'*60}\n")


# ══════════════════════════════════════════════════════════════
#  SECTION 6 — ENTRY POINT
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Equity Research Assistant")
    parser.add_argument("--stocks", help="Comma-separated tickers, e.g. RELIANCE.NS,TCS.NS")
    parser.add_argument("--file",   help="Text file with one ticker per line", default="stocks.txt")
    parser.add_argument("--output", help="Save JSON output to file", default=None)
    args = parser.parse_args()

    if args.stocks:
        tickers = [t.strip() for t in args.stocks.split(",")]
    else:
        try:
            with open(args.file) as f:
                tickers = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        except FileNotFoundError:
            # Demo tickers
            tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "WIPRO.NS",
                       "ICICIBANK.NS", "BAJFINANCE.NS", "TATAMOTORS.NS", "ADANIENT.NS", "MARUTI.NS"]

    report = run_daily_analysis(tickers)

    # Path fix: ensure default is in reports/ relative to script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    reports_dir = os.path.join(base_dir, "reports")
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    default_name = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    output_path = args.output or os.path.join(reports_dir, default_name)

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"✅ Full JSON report saved to: {os.path.abspath(output_path)}")
