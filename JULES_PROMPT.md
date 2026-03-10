# ══════════════════════════════════════════════════════════════
#  PROMPT FOR GOOGLE JULES (or Gemini Code Assist / Cursor)
#  Use this after opening the stock_engine/ folder in your IDE
# ══════════════════════════════════════════════════════════════

## HOW TO OPEN THE PROJECT IN JULES
1. Download all files from Claude → they will be in a folder called stock_engine/
2. Open Jules at https://jules.google.com
3. Click "New Task" → Connect your GitHub repo OR upload the folder
4. Paste the prompt below into the Jules task input

---

## ✅ MASTER PROMPT (paste this into Jules)

```
I have a Python-based equity stock research assistant. 
The project folder contains:
- indicator_engine.py   (main analysis engine, 30+ technical indicators)
- config_loader.py      (config reader module)  
- config.json           (master configuration file)
- n8n_workflow.json     (n8n automation workflow)
- stocks.txt            (stock ticker list)

Please do the following tasks:

─────────────────────────────────────────────────────────────
TASK 1 — Wire config.json into indicator_engine.py
─────────────────────────────────────────────────────────────
At the top of indicator_engine.py, add:
  from config_loader import CFG

Replace ALL hardcoded values with CFG lookups:
- RSI period 14          → CFG.ind("rsi_period", 14)
- MACD periods 12,26,9   → CFG.ind("macd_fast"), CFG.ind("macd_slow"), CFG.ind("macd_signal")
- Bollinger period 20    → CFG.ind("bb_period", 20)
- ATR period 14          → CFG.ind("atr_period", 14)
- Stochastic period 14   → CFG.ind("stoch_period", 14)
- SuperTrend 10, 3.0     → CFG.ind("supertrend_period"), CFG.ind("supertrend_mult")
- Volume spike ratio 1.5 → CFG.ind("volume_spike_ratio", 1.5)
- All scoring bonuses    → CFG.rule("rsi_bullish_zone_bonus") etc.
- Scoring weights        → CFG.weights()["technical"] etc.
- Signal thresholds      → CFG.signal_for_score(score)
- Stock list             → CFG.stocks() instead of reading stocks.txt
- history_period         → CFG["data"]["history_period"]
- top_picks_count        → CFG["output"]["top_picks_count"]

─────────────────────────────────────────────────────────────
TASK 2 — Add a Web UI config editor (optional Streamlit app)
─────────────────────────────────────────────────────────────
Create a new file called config_editor.py using Streamlit:
- Tab 1 "Stocks": 
    Show current stock list with checkboxes to remove stocks.
    Text input to add new tickers. 
    Dropdown to choose market (India NSE / India BSE / US).
    Save button that writes back to config.json.
    
- Tab 2 "Scoring Weights":
    Four sliders (Technical, Volume, Event, Fundamental).
    Auto-normalize so they always sum to 1.0.
    Live preview showing what score a sample stock would get.
    
- Tab 3 "Indicator Params":
    Sliders for RSI period (5–30), MACD periods, BB period.
    Number inputs for multipliers and thresholds.
    
- Tab 4 "Scoring Rules":
    Sliders from -30 to +30 for every bonus/penalty in config.json.
    Group them by category: RSI rules, MACD rules, Volume rules.
    
- Tab 5 "Run Analysis":
    Button to run indicator_engine.py with current config.
    Show output as a formatted table with color-coded signals.
    Download button to save the JSON report.

Run with: streamlit run config_editor.py

─────────────────────────────────────────────────────────────
TASK 3 — Add validation to config_loader.py
─────────────────────────────────────────────────────────────
Add a validate() method to the Config class that:
- Checks scoring_weights sum to exactly 1.0 (raise ValueError if not)
- Checks all tickers are non-empty strings
- Checks all period values are positive integers
- Checks all threshold values are in 0–100 range and in ascending order
- Prints a clear warning for each invalid value
- Returns True if valid, False if invalid (don't crash — warn and use defaults)

─────────────────────────────────────────────────────────────
TASK 4 — Update n8n_workflow.json
─────────────────────────────────────────────────────────────
In the "🔧 Parse Ticker List" node JavaScript code:
- Instead of reading from a file, read the stock list from a 
  JSON input that matches the config.json "stocks" structure.
- Support both India NSE, India BSE, and US stocks arrays.
- Add a filter to skip empty strings.

In the "📊 Compute Indicators (JS)" node:
- Add a configParams object at the top of the JS code with all
  indicator params (rsi_period, macd_fast, etc.) so they can
  be edited directly in the n8n node without touching Python.

─────────────────────────────────────────────────────────────
TASK 5 — Add a daily summary email template
─────────────────────────────────────────────────────────────
Create email_template.py that generates a rich HTML email:
- Subject: "📊 Daily Equity Briefing — {date} | {strong_buys} Strong Buys"
- Header with date and market breadth bar chart (use inline SVG)
- Section 1: TOP MOMENTUM table (ticker, score bar, signal badge, 1D change)
- Section 2: AVOID LIST table (same columns, red theme)
- Section 3: KEY EVENTS UPCOMING (earnings dates in next 14 days)
- Footer: "Generated by Equity Research Assistant"
- All CSS must be inline (for email clients)
- Function: generate_html_email(report_dict) → returns HTML string

All output files should use the same folder structure. 
Do not change indicator_engine.py logic, only wire in config values.
After changes, run: python indicator_engine.py --stocks TCS.NS,INFY.NS
to verify it works.
```

---

## 💡 TIPS FOR USING JULES

- Jules works best with tasks broken into numbered steps (as above)
- After Jules makes changes, ask: "Now run the script and show me the output"
- If Jules misses something: "In Task 1, you didn't replace the scoring weights — please fix that"
- Jules can commit directly to GitHub — connect your repo for one-click deploy

## FOR CURSOR / WINDSURF / GITHUB COPILOT WORKSPACE
Same prompt works. Just open the folder, hit Ctrl+I (Cursor) or the 
chat panel, and paste. These IDEs have file context so they'll see all files automatically.
