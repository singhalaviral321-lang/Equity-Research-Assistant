# ╔══════════════════════════════════════════════════════════════╗
# ║       EQUITY RESEARCH ASSISTANT — SETUP GUIDE              ║
# ╚══════════════════════════════════════════════════════════════╝

## 📁 FILES IN THIS PACKAGE

```
stock_engine/
├── indicator_engine.py   ← Main Python analysis engine (30+ indicators)
├── n8n_workflow.json     ← Import this directly into n8n
├── dashboard.jsx         ← React dashboard (paste into Claude.ai or deploy)
├── stocks.txt            ← Your daily stock pool (edit this)
└── SETUP.md              ← This file
```

---

## 🚀 QUICK START (5 Steps)

### Step 1 — Install Python Dependencies
```bash
pip install yfinance pandas numpy ta requests python-dotenv
```

### Step 2 — Edit Your Stock Pool
Open `stocks.txt` and add your tickers:
- Indian stocks: RELIANCE.NS, TCS.NS, HDFCBANK.BO
- US stocks: AAPL, MSFT, NVDA
- Crypto (via Yahoo): BTC-USD, ETH-USD

### Step 3 — Run Analysis Manually
```bash
# Analyze from stocks.txt
python indicator_engine.py

# Pass tickers directly
python indicator_engine.py --stocks RELIANCE.NS,TCS.NS,INFY.NS

# Save output
python indicator_engine.py --output today_report.json
```

### Step 4 — Set Up n8n
```bash
# Install n8n via Docker (free, self-hosted)
docker run -it --rm --name n8n -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Open browser: http://localhost:5678
# Import n8n_workflow.json via: Settings → Import Workflow
```

### Step 5 — Configure n8n Credentials
In n8n, set these environment variables:
```
TELEGRAM_CHAT_ID=your_chat_id        # Get from @userinfobot
GOOGLE_SHEET_ID=your_sheet_id        # From Google Sheets URL
WEBHOOK_URL=http://your-dashboard    # Optional
```

---

## 📊 INDICATORS INCLUDED

### Momentum (7)
- RSI (14) with signal zones
- Stochastic %K/%D
- Williams %R
- CCI (20)
- ROC (10, 20)
- MFI (14) — volume weighted RSI
- Momentum Oscillator

### Trend (8)
- MACD + Signal + Histogram + Crossover detection
- SMA 20/50/200
- EMA 9/21/50
- ADX (14) with strength label
- Golden/Death Cross detection
- SuperTrend (10,3)
- Parabolic SAR signal
- Price vs all key MAs (% deviation)

### Volatility (4)
- Bollinger Bands (upper/lower/width/position)
- ATR (14) absolute + percentage
- BB Squeeze detection
- Historical volatility proxy

### Volume (5)
- OBV with trend direction
- Volume Ratio vs 20-day average
- Volume spike detection
- Chaikin Money Flow (20)
- MFI (Money Flow Index)

### Price Levels (6)
- Daily Pivot Points (P, R1, R2, S1, S2)
- 52-week High/Low % proximity
- Fibonacci levels (via pivot)
- VWAP (intraday, if available)

---

## 🎯 SCORING SYSTEM

```
Composite Score = 
  Technical Score  × 45%  (RSI, MACD, MAs, BB, SuperTrend)
  Volume Score     × 25%  (OBV, CMF, Volume spikes, MFI)
  Event Score      × 15%  (Analyst rating, earnings proximity)
  Fundamental Score× 15%  (PE, PB, dividend yield, analyst target)

Score → Signal:
  72–100  →  STRONG BUY  🟢🟢
  58–71   →  BUY         🟢
  42–57   →  NEUTRAL     🟡
  28–41   →  SELL        🔴
  0–27    →  STRONG SELL 🔴🔴
```

---

## 📅 EVENT TRACKING

### Automated via Yahoo Finance (free, no key)
- Earnings dates (auto-detected)
- Dividend ex-dates
- Stock splits

### Via Finnhub (free tier — 60 calls/min)
```python
# Add to your .env:
FINNHUB_API_KEY=your_free_key
```
- Analyst upgrades/downgrades
- Insider transactions
- Company news with sentiment

### Macro Events (manual or scrape)
- Add to a Google Sheet column "upcoming_events"
- n8n reads and factors into scoring

---

## 📱 TELEGRAM SETUP

1. Message @BotFather → /newbot → get TOKEN
2. Message @userinfobot → get your CHAT_ID
3. Set in n8n:
   - Telegram credential: paste TOKEN
   - TELEGRAM_CHAT_ID env var: paste CHAT_ID

Sample daily message format:
```
📊 DAILY EQUITY BRIEFING — 15 Jan 2025

🟢 STRONG BUY (4): RELIANCE, TCS, BAJFINANCE, HDFCBANK
🟢 BUY (6): INFY, IRCTC, ZOMATO...
🟡 NEUTRAL (7): WIPRO, ICICIBANK...
🔴 SELL (3): ADANIENT, PAYTM, POLICYBZR

🚀 TOP PICK: RELIANCE.NS Score:81
  • MACD bullish crossover
  • Volume 1.8x average
  ₹2847 ▲+2.14%

⚠️ AVOID: PAYTM.NS Score:28
  ⚡ Heavy volume selling
  ₹412 ▼-3.21%
```

---

## 🔧 CUSTOMIZATION

### Change analysis timing
In n8n trigger, change cron:
```
0 18 * * 1-5   →  6:00 PM weekdays (default)
0 9  * * 1-5   →  9:00 AM pre-market
0 15 * * 1-5   →  3:00 PM intraday check
```

### Add custom indicators
In `indicator_engine.py`, Section 2 — add your logic:
```python
# Example: Add Fibonacci levels
fib_0618 = float(high_52w - (high_52w - low_52w) * 0.618)
ind["fib_618"] = round(fib_0618, 2)
```

### Adjust scoring weights
In `score_stock()`:
```python
composite = (
    tech_score   * 0.45 +   # ← change weights here
    vol_score    * 0.25 +
    event_score  * 0.15 +
    fundam_score * 0.15
)
```

---

## 💡 PRO TIPS

1. **For Indian markets**: Use `.NS` suffix (NSE) for most liquid stocks
2. **Rate limiting**: Yahoo Finance allows ~2000 requests/hour. For 50 stocks × 2 API calls = fine
3. **Better data**: Upgrade to Alpha Vantage paid ($50/mo) for real-time intraday
4. **Options flow**: Add Sensibull API (India) or Unusual Whales (US) for smart money signals
5. **Backtesting**: Export JSON results and run against historical data

---

## 🆓 TOTAL COST: ₹0/month

| Service       | Free Tier               |
|---------------|-------------------------|
| n8n           | Self-hosted, unlimited  |
| Yahoo Finance | Unlimited (unofficial)  |
| Finnhub       | 60 calls/min            |
| Telegram Bot  | Unlimited messages      |
| Google Sheets | 15GB storage            |
| Python/TA-lib | Open source             |

---
Built with ❤️ using n8n + Python + Yahoo Finance
