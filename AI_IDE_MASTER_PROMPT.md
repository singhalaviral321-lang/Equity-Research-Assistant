# ╔══════════════════════════════════════════════════════════════════╗
# ║         MASTER AI IDE DEPLOYMENT PROMPT                        ║
# ║         Equity Research Assistant — Full Auto Deploy           ║
# ║                                                                ║
# ║  HOW TO USE THIS FILE:                                         ║
# ║  1. Download ALL files from Claude into one folder             ║
# ║  2. Open that folder in your AI IDE                            ║
# ║     - Jules   : jules.google.com → New Task → attach folder    ║
# ║     - Cursor  : File → Open Folder → then Ctrl+I              ║
# ║     - Windsurf: File → Open Folder → then Cmd/Ctrl+L          ║
# ║     - Copilot : Open folder in VS Code → Copilot Chat          ║
# ║  3. Copy EVERYTHING between the ═══ lines below               ║
# ║  4. Paste it as your first message to the AI                   ║
# ╚══════════════════════════════════════════════════════════════════╝


# ════════════════════════════════════════════════════════════════════
# START OF PROMPT — COPY FROM HERE
# ════════════════════════════════════════════════════════════════════

You are a senior DevOps and Python engineer. I have an Equity Stock 
Research Assistant project in this folder. Your job is to fully deploy 
it so it runs automatically every day, sends me notifications, and 
serves a live dashboard on a public URL — even when my laptop is 
shut down.

Read every file in this folder carefully before doing anything.

Here is a summary of what each file does:
- indicator_engine.py  → Core Python engine. Fetches stock data from 
                          Yahoo Finance, computes 30+ indicators (RSI, 
                          MACD, Bollinger, ADX, SuperTrend, OBV etc.), 
                          scores each stock 0-100, outputs a JSON report.
- config.json          → Master config. Controls stock list, scoring 
                          weights, indicator params, signal thresholds.
- config_loader.py     → Reads config.json and provides CFG helpers 
                          to indicator_engine.py.
- dashboard.jsx        → React dashboard component (reference design).
- n8n_workflow.json    → n8n automation workflow (reference).
- stocks.txt           → Stock ticker pool.

════════════════════════════════════════════════════════════════════
CONTEXT — READ THIS BEFORE WRITING ANY CODE
════════════════════════════════════════════════════════════════════

My situation:
- I am on Windows (assume Windows 11 unless you detect otherwise)
- My laptop shuts down sometimes so I need cloud-based scheduling
- I want a public dashboard URL I can share with others
- I want notifications on Telegram + Gmail + WhatsApp daily
- I want everything FREE (no paid services)
- I am NOT a developer — every step must be explained simply
- After you make all changes, give me exact commands to run, 
  in exact order, with no steps skipped

My target architecture:
  GitHub (stores code + daily report JSONs)
       │
       ├── GitHub Actions (free cloud cron — runs analysis 
       │   daily at 6PM IST even when laptop is OFF)
       │   → Saves report JSON to GitHub repo
       │   → Triggers Telegram + Gmail + WhatsApp notifications
       │
       └── Railway.app (free hosting — always-on dashboard)
             Reads latest JSON from repo
             Public URL: https://myapp.railway.app


════════════════════════════════════════════════════════════════════
TASK 1 — CREATE server.py
════════════════════════════════════════════════════════════════════

Create a file called server.py using Flask. It must:

1. Serve dashboard.html at the root route GET /
2. GET  /api/latest   → Read the most recent JSON file from the 
                         reports/ folder and return it as JSON.
                         If no reports exist, return a helpful error.
3. POST /api/run      → Run indicator_engine.py as a subprocess,
                         save output to reports/analysis_YYYYMMDD_HHMM.json
                         Return {"status": "ok"} when done.
4. GET  /api/config   → Return contents of config.json
5. POST /api/config   → Accept JSON body, write it to config.json, 
                         return {"status": "saved"}
6. GET  /api/history  → Return list of last 30 report filenames 
                         from the reports/ folder

Important details:
- Use flask and flask-cors
- Read PORT from environment variable (default 8050)
- The reports/ folder may not exist — create it if missing
- Print a clear startup message showing the URL
- All routes must handle exceptions gracefully with JSON error responses


════════════════════════════════════════════════════════════════════
TASK 2 — CREATE dashboard.html
════════════════════════════════════════════════════════════════════

Create a single self-contained dashboard.html file. No build step,
no npm, no node — it must work by just opening the file or serving
it from Flask. Use React via CDN + Tailwind via CDN + Babel standalone.

The dashboard must:
1. On load, call fetch("/api/latest") to get the report JSON
2. Show a loading spinner while fetching
3. Show a clear error message if the API fails, with a Retry button
4. Auto-refresh the data every 5 minutes silently
5. Display:
   a) Top navigation bar with app name, date, live indicator dot, 
      and a manual Refresh button
   b) Four summary cards: Strong Buy / Buy / Neutral / Sell — 
      each shows count, a mini score bar, and clicking filters the list
   c) Search box to filter by ticker name
   d) Sort buttons: Score ↓ | 1D% ↓ | A-Z
   e) Stock list — each row shows:
      - Ticker + company name
      - Signal badge (color coded: green/amber/red)
      - Score bar (0-100)
      - Price + 1-day % change
      - RSI semicircle gauge
   f) Clicking a stock opens a detail panel on the right showing:
      - All key indicators (RSI, MACD, SuperTrend, Volume, OBV, ADX)
      - Bullish reasons list (green checkmarks)
      - Risk factors list (red lightning bolts)
      - Pivot points (S1, S2, R1, R2)

Design requirements:
- Dark theme (#09090b background)
- Monospace font (DM Mono or Fira Code from Google Fonts)
- Green (#10b981) as the primary accent color
- Must look professional and be mobile-friendly
- No purple gradients, no generic AI aesthetics


════════════════════════════════════════════════════════════════════
TASK 3 — CREATE run_daily.py
════════════════════════════════════════════════════════════════════

Create run_daily.py — the script that GitHub Actions will call daily.

It must do these things IN ORDER:
1. Run indicator_engine.py and save output to 
   reports/analysis_YYYYMMDD_HHMM.json
2. Send a Telegram message
3. Send a Gmail email  
4. Send a WhatsApp message via CallMeBot API
5. Print a clear log of each step success/failure

All credentials must be read from environment variables:
  TELEGRAM_TOKEN        → Telegram bot token from @BotFather
  TELEGRAM_CHAT_ID      → Your chat ID from @userinfobot
  GMAIL_USER            → your Gmail address
  GMAIL_APP_PASSWORD    → 16-char app password (not your real password)
  GMAIL_TO              → recipient email (can be same as GMAIL_USER)
  WHATSAPP_PHONE        → phone number with country code, no + sign
  WHATSAPP_APIKEY       → API key from CallMeBot

Each notification must GRACEFULLY SKIP if its env vars are missing
(don't crash — just print "Telegram not configured, skipping").

Telegram message format:
  📊 Daily Equity Briefing — {date}
  ══════════════════════
  🟢 Strong Buy: X  |  Buy: X
  🟡 Neutral: X     |  🔴 Sell: X
  
  🚀 Top Picks:
  ✅ RELIANCE  Score:81  ▲2.1%
  ✅ TCS       Score:76  ▲1.4%
  
  ⚠️ Avoid:
  🔴 PAYTM     Score:28  ▼3.2%
  
  🔗 Dashboard: {DASHBOARD_URL env var}

Gmail subject: "📊 Daily Equity Briefing — {date} | {N} Strong Buys"
Gmail body: same content as Telegram but plain text, nicely formatted.

WhatsApp: same as Telegram message (CallMeBot accepts plain text).


════════════════════════════════════════════════════════════════════
TASK 4 — CREATE .github/workflows/daily_analysis.yml
════════════════════════════════════════════════════════════════════

Create the GitHub Actions workflow file at exactly this path:
  .github/workflows/daily_analysis.yml

It must:
1. Trigger on schedule: cron '30 12 * * 1-5' 
   (this is 12:30 PM UTC = 6:00 PM IST, weekdays only)
2. Also have workflow_dispatch so I can trigger it manually 
   from the GitHub website with one click
3. Steps:
   a) Checkout the repo (actions/checkout@v4)
   b) Set up Python 3.11 (actions/setup-python@v5)
   c) Cache pip dependencies for faster runs
   d) Install: pip install -r requirements.txt
   e) Run: python run_daily.py
   f) Commit and push any new files in reports/ back to the repo
      Use these git settings:
        git config user.name  "Stock Research Bot"  
        git config user.email "bot@stock-research.com"
      Only commit if there are actual changes (check with git diff)
      Commit message: "📊 Daily analysis {date}"
   
4. Environment variables must come from GitHub Secrets:
   TELEGRAM_TOKEN, TELEGRAM_CHAT_ID,
   GMAIL_USER, GMAIL_APP_PASSWORD, GMAIL_TO,
   WHATSAPP_PHONE, WHATSAPP_APIKEY,
   DASHBOARD_URL

5. Add a step to create the reports/ directory if it doesn't exist.

6. If the analysis fails, still try to send a Telegram alert saying
   "❌ Daily analysis FAILED — check GitHub Actions logs"


════════════════════════════════════════════════════════════════════
TASK 5 — CREATE Procfile and railway.json
════════════════════════════════════════════════════════════════════

Create Procfile (no extension, exactly this content):
  web: python server.py

Create railway.json:
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": { "builder": "NIXPACKS" },
  "deploy": {
    "startCommand": "python server.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}

Create render.yaml (backup hosting option):
services:
  - type: web
    name: equity-research-assistant
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python server.py
    envVars:
      - key: PORT
        value: 10000
      - key: TELEGRAM_TOKEN
        sync: false
      - key: TELEGRAM_CHAT_ID
        sync: false
      - key: GMAIL_USER
        sync: false
      - key: GMAIL_APP_PASSWORD
        sync: false
      - key: GMAIL_TO
        sync: false
      - key: DASHBOARD_URL
        sync: false


════════════════════════════════════════════════════════════════════
TASK 6 — UPDATE requirements.txt
════════════════════════════════════════════════════════════════════

Create/overwrite requirements.txt with exactly these packages
and minimum versions:

  yfinance>=0.2.36
  pandas>=2.0.0
  numpy>=1.24.0
  ta>=0.11.0
  requests>=2.31.0
  flask>=3.0.0
  flask-cors>=4.0.0
  python-dotenv>=1.0.0


════════════════════════════════════════════════════════════════════
TASK 7 — CREATE .env.template
════════════════════════════════════════════════════════════════════

Create .env.template (I will copy this to .env and fill in values):

# ── Telegram ──────────────────────────────────
TELEGRAM_TOKEN=your_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_chat_id_from_userinfobot

# ── Gmail ─────────────────────────────────────
GMAIL_USER=youremail@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
GMAIL_TO=youremail@gmail.com

# ── WhatsApp (via CallMeBot) ───────────────────
WHATSAPP_PHONE=91XXXXXXXXXX
WHATSAPP_APIKEY=your_callmebot_apikey

# ── Dashboard ─────────────────────────────────
DASHBOARD_URL=https://your-app.railway.app

# ── Server ────────────────────────────────────
PORT=8050

Also create .gitignore with:
  .env
  __pycache__/
  *.pyc
  .DS_Store
  reports/*.json


════════════════════════════════════════════════════════════════════
TASK 8 — WIRE config.json INTO indicator_engine.py
════════════════════════════════════════════════════════════════════

Modify indicator_engine.py to use config_loader.py:

1. At the top, add: from config_loader import CFG
   Wrap in try/except so it works even if config.json is missing.

2. Replace these hardcoded values with CFG lookups:
   - RSI period 14            → CFG.ind("rsi_period", 14)
   - MACD 12,26,9             → CFG.ind("macd_fast",12), CFG.ind("macd_slow",26), CFG.ind("macd_signal",9)
   - Bollinger period 20      → CFG.ind("bb_period", 20)
   - ATR period 14            → CFG.ind("atr_period", 14)
   - Stochastic period 14     → CFG.ind("stoch_period", 14)
   - CCI period 20            → CFG.ind("cci_period", 20)
   - ADX period 14            → CFG.ind("adx_period", 14)
   - SuperTrend 10, 3.0       → CFG.ind("supertrend_period",10), CFG.ind("supertrend_mult",3.0)
   - Volume spike 1.5         → CFG.ind("volume_spike_ratio", 1.5)
   - history period "6mo"     → CFG["data"].get("history_period","6mo")
   - top_picks_count 5        → CFG["output"].get("top_picks_count", 5)

3. In score_stock(), replace all hardcoded bonus/penalty numbers 
   with CFG.rule() calls:
   - rsi_bullish_zone_bonus, rsi_oversold_penalty, etc.
   - All scoring weights: CFG.weights()["technical"] etc.
   - Signal thresholds: use CFG.signal_for_score(score)

4. In run_daily_analysis(), get tickers from CFG.stocks() 
   instead of the tickers argument (keep argument as override).

5. Do NOT change any of the mathematical logic — only replace 
   hardcoded literals with config lookups.


════════════════════════════════════════════════════════════════════
TASK 9 — CREATE STEP-BY-STEP SETUP GUIDE
════════════════════════════════════════════════════════════════════

After completing all code tasks, create a file called DEPLOY_NOW.md
with a clear, numbered, copy-paste-ready guide for a non-developer.
It must cover:

PART A — One-time setup (do once)
  A1. Install Python on Windows (with PATH checkbox warning)
  A2. Install Git on Windows (git-scm.com)
  A3. Create a free GitHub account and new repo
  A4. Push this folder to GitHub (exact git commands)
  A5. Create free Railway account, connect GitHub repo, set env vars
  A6. Set up GitHub Secrets (exact steps with screenshots described)
  A7. Set up Telegram bot (exact @BotFather steps)
  A8. Set up Gmail App Password (exact Google account steps)
  A9. Set up WhatsApp CallMeBot (exact steps)

PART B — Daily operation (happens automatically)
  B1. What happens at 6PM IST every weekday (automated)
  B2. How to check if it ran successfully (GitHub Actions tab)
  B3. How to trigger it manually (workflow_dispatch button)
  B4. How to change your stock list (edit config.json, commit, push)
  B5. How to access the dashboard

PART C — Troubleshooting
  C1. "No reports found" error on dashboard
  C2. GitHub Actions failed (where to see logs)
  C3. Telegram not receiving messages
  C4. Railway dashboard showing old data
  C5. How to add/remove stocks

Format rules for DEPLOY_NOW.md:
- Use emoji headers for each section
- Every command must be in a code block
- Never assume the reader knows what "clone" or "push" means
- Explain every term on first use in plain English


════════════════════════════════════════════════════════════════════
TASK 10 — VERIFICATION AND TESTING
════════════════════════════════════════════════════════════════════

After creating all files:

1. Check that indicator_engine.py still imports cleanly by looking 
   for any syntax errors or broken imports you may have introduced.

2. Verify that the .github/workflows/daily_analysis.yml is valid YAML
   by checking indentation carefully.

3. Check that dashboard.html has no broken JavaScript — look for 
   unclosed brackets, missing semicolons, or undefined variables.

4. Confirm that server.py has routes for /, /api/latest, /api/run,
   /api/config, /api/history.

5. Print a final summary of ALL files you created or modified, 
   with one line describing what each one does.


════════════════════════════════════════════════════════════════════
FINAL OUTPUT FORMAT
════════════════════════════════════════════════════════════════════

When you are done with all tasks, end your response with:

--- DEPLOYMENT READY CHECKLIST ---
[ ] server.py created
[ ] dashboard.html created  
[ ] run_daily.py created
[ ] .github/workflows/daily_analysis.yml created
[ ] Procfile created
[ ] railway.json created
[ ] render.yaml created
[ ] requirements.txt updated
[ ] .env.template created
[ ] .gitignore created
[ ] indicator_engine.py updated (config wired in)
[ ] DEPLOY_NOW.md created

NEXT STEP FOR YOU:
Run this single command to install everything and test locally:
  pip install -r requirements.txt && python indicator_engine.py --stocks TCS.NS && python server.py

Then follow DEPLOY_NOW.md for the full cloud deployment.

# ════════════════════════════════════════════════════════════════════
# END OF PROMPT
# ════════════════════════════════════════════════════════════════════
