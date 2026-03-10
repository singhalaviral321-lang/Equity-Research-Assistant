# 📊 Equity Research Assistant
### AI-Powered Daily Stock Analysis · Free · Automated · Agentic

> Reads the charts. Reads the news. Remembers what happened before.  
> Sends you a clear daily briefing in plain English — every weekday at 6PM IST.  
> **Total cost: ₹0/month.**

---

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![Groq](https://img.shields.io/badge/AI-Groq%20Llama%203.3-F55036?style=flat)
![Yahoo Finance](https://img.shields.io/badge/Data-Yahoo%20Finance-6001D2?style=flat)
![GitHub Actions](https://img.shields.io/badge/Scheduler-GitHub%20Actions-2088FF?style=flat&logo=github-actions&logoColor=white)
![Render](https://img.shields.io/badge/Hosted%20on-Render-46E3B7?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

---

## 🧠 What Is This?

Most retail investors either spend hours manually reading charts every evening, or rely on expensive research subscriptions (₹5,000–₹15,000/month) that still don't explain *why* a stock is worth watching today.

**This project eliminates both problems.**

It is a fully automated, AI-powered equity research assistant that:
- Fetches live price data for your personal stock watchlist
- Computes **30+ technical indicators** per stock
- Searches and reads **today's news** for each stock
- Uses a **free AI model (Groq / Llama 3.3 70B)** to reason about each stock like a senior analyst
- Remembers its past analysis and **detects pattern changes** over time
- Sends you a **beautiful daily briefing** via Telegram, Gmail, and WhatsApp
- Serves a **live interactive dashboard** on a public URL

All of this runs automatically every weekday — even when your laptop is off.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR CONFIGURATION                      │
│         config.json — stocks, weights, parameters           │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │    GitHub Actions       │
              │  Runs daily 6PM IST     │
              │  Free · Always on       │
              └────────────┬────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
  📡 Data Layer     📰 News Layer      🧠 AI Layer
  Yahoo Finance     Google News RSS    Groq (Free)
  30+ Indicators    ET Markets RSS     Llama 3.3 70B
  Scoring Engine    Yahoo Finance      Gemini Fallback
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
              ┌────────────▼────────────┐
              │     Memory Bank         │
              │  Streaks · Reversals    │
              │  30-day history/stock   │
              └────────────┬────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
    📱 Telegram       📧 Gmail          💬 WhatsApp
    Formatted         HTML Report       Via CallMeBot
    Daily Brief       Full Analysis     Quick Summary
         │
         ▼
  🌐 Live Dashboard (Render)
  Public URL · Always Online
  Interactive · Mobile Friendly
```

---

## ✨ Features

### 📊 Technical Analysis Engine
Computes 30+ indicators across 5 categories:

| Category | Indicators |
|---|---|
| **Momentum** | RSI (14), Stochastic %K/%D, Williams %R, CCI, ROC, MFI |
| **Trend** | MACD + Histogram, ADX, SuperTrend, Parabolic SAR, Golden/Death Cross |
| **Moving Averages** | SMA 20/50/200, EMA 9/21/50, DEMA, Price vs DMA % |
| **Volatility** | Bollinger Bands, ATR, BB Squeeze detection |
| **Volume** | OBV, CMF, Volume Spike ratio, MFI, Accumulation/Distribution |
| **Price Levels** | Daily Pivot Points (P/R1/R2/S1/S2), 52W High/Low proximity |

### 🤖 AI Analysis (Free — Groq)
- Powered by **Llama 3.3 70B** via Groq API (free tier, no credit card)
- Reads technical indicators + today's news together
- Gives **plain English verdict** with reasoning
- Identifies **key risk** and **key catalyst** per stock
- Suggests **time horizon** (short/medium/long term)
- Falls back to **Google Gemini** (also free) if Groq is unavailable

### 🧬 Memory & Pattern Detection
- Remembers verdicts for **last 30 days** per stock
- Detects **streaks** — "Bearish 4 days straight"
- Detects **reversals** — "🔄 Turned bullish after 3 down days"
- Alerts you when something **genuinely changed** today
- AI references memory in its reasoning — context-aware analysis

### 📰 News Intelligence
- Searches **Google News RSS** (free, no key)
- Reads **Yahoo Finance** headlines
- Reads **Economic Times Markets RSS** (free)
- Tags headlines as positive/negative/neutral
- Passes news context to AI before analysis

### 🎛️ Fully Configurable
Everything controlled via `config.json` — no code changes needed:
- Which stocks to analyze
- Scoring weights (technical/volume/event/fundamental)
- All indicator parameters (RSI period, MACD settings etc.)
- Signal thresholds (what score = BUY vs SELL)
- Schedule, output settings, notification preferences

---

## 📱 Daily Briefing Preview

### Telegram Message
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 EQUITY BRIEFING  10 Mar 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌡️ MARKET PULSE
🟢 Strong Buy : 4    🟢 Buy    : 6
🟡 Neutral   : 7    🔴 Sell   : 3
📈 Avg Score : 54/100

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 TOP PICKS TODAY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 RELIANCE · ₹2,847 · +2.14%
   Score  : 81/100 ████████████
   Signal : STRONG BUY  |  RSI: 62
   🤖 "Breakout confirmed with institutional volume"
   ⏱️  Horizon : MEDIUM (1-3 weeks)
   🎯 Catalyst: Jio subscriber growth beat

🏆 BAJFINANCE · ₹7,140 · +3.21%
   Score  : 74/100 █████████░░░
   Signal : STRONG BUY  |  RSI: 64
   🤖 "Reversed bullish after 2 down days"
   ⏱️  Horizon : SHORT (1-3 days)
   🎯 Catalyst: Credit growth data due Friday

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  AVOID TODAY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 PAYTM · ₹412 · -3.21%
   Score  : 28/100 ███░░░░░░░░░
   🤖 "Regulatory overhang killing momentum"
   ⚡ Risk : RBI scrutiny continues

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 AI PATTERN ALERTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 WIPRO: Bearish 5 days straight
📌 BAJFINANCE: 🔄 Reversed bullish today
📌 ADANIENT: Score dropped 22 points — unusual

📅 WATCH THIS WEEK
📆 TCS — Earnings Thursday

🔗 Dashboard → https://yourapp.render.com
⏰ Next update: Tomorrow 6PM IST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🗂️ Project Structure

```
equity-research-assistant/
│
├── 📊 Core Engine
│   ├── indicator_engine.py    # 30+ technical indicators + scoring
│   ├── config_loader.py       # Reads and validates config.json
│   └── config.json            # YOUR master control panel
│
├── 🤖 AI Layer
│   ├── ai_analyst.py          # Groq AI reasoning engine
│   ├── news_fetcher.py        # Free news from RSS + Yahoo
│   └── memory_store.py        # 30-day memory per stock
│
├── 🌐 Dashboard
│   ├── server.py              # Flask API server
│   └── dashboard.html         # Interactive web dashboard
│
├── ⚙️ Automation
│   ├── run_daily.py           # Orchestrates full pipeline
│   └── .github/workflows/
│       └── daily_analysis.yml # GitHub Actions cron job
│
├── 🚀 Deployment
│   ├── Procfile               # Railway/Render start command
│   ├── railway.json           # Railway config
│   ├── render.yaml            # Render config
│   └── requirements.txt       # Python dependencies
│
├── 📁 Data
│   ├── stocks.txt             # Your stock watchlist
│   └── reports/               # Daily JSON reports (auto-generated)
│       ├── memory.json        # AI memory bank
│       └── analysis_DATE.json # Daily enriched reports
│
└── 📖 Documentation
    ├── README.md              # This file
    ├── DEPLOY_NOW.md          # Step-by-step deployment guide
    └── AI_IDE_MASTER_PROMPT.md # Prompt to set up with any AI IDE
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Git
- Free accounts: GitHub, Render, Groq, Telegram

### 1. Clone & Install
```bash
git clone https://github.com/YOUR_USERNAME/equity-research-assistant.git
cd equity-research-assistant
pip install -r requirements.txt
```

### 2. Configure Your Stocks
Edit `config.json`:
```json
{
  "stocks": {
    "india_nse": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"],
    "us_stocks": ["AAPL", "NVDA"]
  },
  "scoring_weights": {
    "technical": 0.45,
    "volume": 0.25,
    "event": 0.15,
    "fundamental": 0.15
  }
}
```

### 3. Set Environment Variables
```bash
cp .env.template .env
# Edit .env with your credentials
```

### 4. Run First Analysis
```bash
python indicator_engine.py
python server.py
# Open http://localhost:8050
```

### 5. Deploy to Cloud (Free)
Follow `DEPLOY_NOW.md` for full step-by-step instructions.

---

## ⚙️ Configuration Reference

All settings live in `config.json`. **You never need to touch Python code.**

```jsonc
{
  // Which stocks to watch
  "stocks": {
    "india_nse": ["RELIANCE.NS", "TCS.NS"],
    "india_bse": [],
    "us_stocks": []
  },

  // How much each factor contributes to the score
  "scoring_weights": {
    "technical":   0.45,  // RSI, MACD, SuperTrend etc.
    "volume":      0.25,  // OBV, CMF, Volume spikes
    "event":       0.15,  // Analyst ratings, earnings
    "fundamental": 0.15   // PE, PB, dividend yield
  },

  // Score → Signal mapping
  "signal_thresholds": {
    "strong_buy": 72,    // score >= 72 = STRONG BUY
    "buy":        58,    // score >= 58 = BUY
    "neutral_low":42,    // score >= 42 = NEUTRAL
    "sell":       28     // score >= 28 = SELL, else STRONG SELL
  },

  // Fine-tune every bonus/penalty
  "scoring_rules": {
    "macd_bullish_cross_bonus": 15,
    "rsi_bullish_zone_bonus":   12,
    "volume_spike_up_bonus":    20
    // ... 20+ more rules
  }
}
```

---

## 🆓 Free Services Used

| Service | Purpose | Free Limit | Link |
|---|---|---|---|
| **Yahoo Finance** | Stock price data | Unlimited | Built-in |
| **Google News RSS** | News headlines | Unlimited | Built-in |
| **Groq API** | AI analysis (Llama 3.3) | 14,400 req/day | console.groq.com |
| **Google Gemini** | AI fallback | 1,500 req/day | aistudio.google.com |
| **GitHub Actions** | Daily scheduler | 2,000 min/month* | github.com |
| **Render** | Dashboard hosting | 750 hrs/month | render.com |
| **UptimeRobot** | Keep Render awake | 50 monitors | uptimerobot.com |
| **Telegram Bot** | Notifications | Unlimited | t.me/BotFather |
| **Gmail SMTP** | Email reports | 500/day | myaccount.google.com |

*Unlimited for public repositories

**Total monthly cost: ₹0**

---

## 📈 Scoring System

Each stock receives a composite score (0–100):

```
Composite Score =
  Technical Score  × 45%   RSI, MACD, ADX, SuperTrend, BB, MAs
  Volume Score     × 25%   OBV, CMF, Volume spikes, MFI
  Event Score      × 15%   Analyst ratings, earnings proximity
  Fundamental Score× 15%   PE ratio, PB, dividend yield, target price

Score → Signal:
  72 – 100  →  🟢🟢 STRONG BUY
  58 – 71   →  🟢   BUY
  42 – 57   →  🟡   NEUTRAL
  28 – 41   →  🔴   SELL
   0 – 27   →  🔴🔴 STRONG SELL
```

---

## 🤖 AI Verdict Structure

For each stock, the AI outputs:
```json
{
  "verdict": "BUY",
  "confidence": "HIGH",
  "agrees_with_signal": true,
  "one_liner": "Breakout confirmed with institutional volume",
  "reasoning": "RSI in healthy 55-65 zone with expanding MACD histogram. Volume 2.1x average confirms institutional participation. Price reclaimed 50 DMA after 3 days below.",
  "key_risk": "Broader market selloff could invalidate breakout",
  "key_catalyst": "Q4 results due next week — street estimates beatable",
  "news_impact": "POSITIVE",
  "time_horizon": "MEDIUM (1-3 weeks)",
  "memory_note": "First bullish signal after 2 neutral days"
}
```

---

## 🔄 How It Works — Daily Flow

```
6:00 PM IST  GitHub Actions wakes up (free, cloud, always on)
     │
6:01 PM  Fetches 6 months OHLCV data per stock (Yahoo Finance)
     │
6:03 PM  Computes 30+ indicators per stock
         Scores each stock 0-100
         Labels: STRONG BUY / BUY / NEUTRAL / SELL / STRONG SELL
     │
6:04 PM  Fetches today's news headlines per stock
         Google News RSS + Yahoo Finance + ET Markets
     │
6:06 PM  For each stock, AI reads:
         → Technical indicators + scores
         → Today's news headlines
         → Last 7 days from memory bank
         → Streak and reversal patterns
         Groq Llama 3.3 70B reasons and responds
     │
6:08 PM  Memory bank updated with today's verdict
         Pattern alerts generated (reversals, streaks)
     │
6:09 PM  Enriched JSON saved → committed to GitHub repo
         Render dashboard auto-updates
     │
6:10 PM  You receive:
         📱 Telegram — formatted mobile brief
         📧 Gmail — full HTML research report
         💬 WhatsApp — quick summary
```

---

## 🛡️ Important Disclaimers

> **This tool is for informational and educational purposes only.**
> 
> - It does **not** provide financial advice
> - It does **not** guarantee profits or predict the future
> - It does **not** have access to your broker or trading account
> - It **cannot** place trades on your behalf
> - All investment decisions remain **entirely yours**
> - Always do your own research before investing
> - Past technical patterns do not guarantee future performance

---

## 🗺️ Roadmap

- [ ] Options chain analysis (Put/Call ratio)
- [ ] FII/DII flow integration (NSE data)
- [ ] Sector rotation detection
- [ ] Portfolio tracker integration
- [ ] WhatsApp via Twilio (more reliable)
- [ ] Streamlit config editor UI
- [ ] Backtesting module
- [ ] Multi-timeframe analysis (weekly + daily)

---

## 🤝 Contributing

Contributions welcome. Please:
1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

For major changes, open an issue first to discuss.

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Acknowledgements

- [yfinance](https://github.com/ranaroussi/yfinance) — Yahoo Finance data
- [ta](https://github.com/bukosabino/ta) — Technical Analysis library
- [Groq](https://groq.com) — Free LLM inference
- [n8n](https://n8n.io) — Workflow automation reference

---

<div align="center">

**Built with ❤️ for retail investors who deserve better tools**

*Star ⭐ this repo if it helps you*

</div>
