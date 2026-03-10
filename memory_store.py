import os
import json
from datetime import datetime

# Path to memory relative to script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(BASE_DIR, "reports", "memory.json")

def _load_memory() -> dict:
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def _save_memory(memory: dict):
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def save_analysis(ticker, date, score, signal, ai_verdict, confidence, price, rsi, reasoning):
    """Saves to memory. Keeps last 30 entries per ticker."""
    memory = _load_memory()
    if ticker not in memory:
        memory[ticker] = {"history": []}
    
    entry = {
        "date": date,
        "score": score,
        "signal": signal,
        "ai_verdict": ai_verdict,
        "ai_confidence": confidence,
        "price": price,
        "rsi": rsi,
        "reasoning": reasoning
    }
    
    # Append to history
    memory[ticker]["history"].append(entry)
    # Keep last 30
    memory[ticker]["history"] = memory[ticker]["history"][-30:]
    
    _save_memory(memory)

def get_history(ticker, days=7) -> list:
    memory = _load_memory()
    if ticker not in memory:
        return []
    # Simplified filtering by days based on list reversal
    return memory[ticker]["history"][-days:]

def get_streak(ticker) -> dict:
    history = get_history(ticker, days=10)
    if not history:
        return {"direction": "NEUTRAL", "days": 0, "message": "No history available"}
    
    last_verdict = history[-1]["ai_verdict"]
    streak = 0
    for h in reversed(history):
        if h["ai_verdict"] == last_verdict:
            streak += 1
        else:
            break
            
    direction = "BULLISH" if last_verdict in ["BUY", "STRONG BUY", "WATCH"] else "BEARISH" if last_verdict == "SELL" else "NEUTRAL"
    return {
        "direction": direction,
        "days": streak,
        "message": f"{direction} for {streak} consecutive days"
    }

def get_trend_change(ticker) -> dict:
    history = get_history(ticker, days=2)
    if len(history) < 2:
        return {"changed": False, "from": None, "to": None, "message": "First analysis", "is_reversal": False}
    
    yest = history[-2]["ai_verdict"]
    today = history[-1]["ai_verdict"]
    
    # Simplified reversal check: went from bearish to bullish OR vice versa
    bearish = ["SELL", "STRONG SELL"]
    bullish = ["BUY", "STRONG BUY"]
    
    is_reversal = (yest in bearish and today in bullish) or (yest in bullish and today in bearish)
    
    if yest != today:
        return {
            "changed": True,
            "from": yest,
            "to": today,
            "message": f"🔄 Changes: {yest} → {today}",
            "is_reversal": is_reversal
        }
    return {"changed": False, "from": yest, "to": today, "message": "No change", "is_reversal": False}

def get_watchlist_alerts(all_tickers) -> list:
    memory = _load_memory()
    alerts = []
    
    for ticker in all_tickers:
        if ticker not in memory or not memory[ticker]["history"]:
            continue
            
        tc = get_trend_change(ticker)
        if tc["changed"]:
            msg = f"Reversed {tc['to'].lower()}" if tc["is_reversal"] else f"Changed to {tc['to'].lower()}"
            alerts.append({"ticker": ticker, "alert": msg, "priority": "HIGH" if tc["is_reversal"] else "MEDIUM"})
        
        streak = get_streak(ticker)
        if streak["days"] >= 4:
            alerts.append({"ticker": ticker, "alert": f"{streak['days']}-day {streak['direction'].lower()} streak", "priority": "MEDIUM"})
            
        # Score jump
        history = memory[ticker]["history"]
        if len(history) >= 2:
            diff = history[-1]["score"] - history[-2]["score"]
            if abs(diff) >= 15:
                alerts.append({
                    "ticker": ticker, 
                    "alert": f"Significant score {'gain' if diff > 0 else 'drop'} (+{diff:.1f} pts)" if diff > 0 else f"Significant score {'gain' if diff > 0 else 'drop'} ({diff:.1f} pts)", 
                    "priority": "HIGH"
                })
                
    return alerts

if __name__ == "__main__":
    # Test
    save_analysis("TCS.NS", "2026-03-10", 41.8, "SELL", "SELL", "HIGH", 3921.00, 21.2, "Bearish technicals")
    print(json.dumps(get_streak("TCS.NS"), indent=2))
