import os
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from indicator_engine import run_daily_analysis

# Level 3 Modules
import news_fetcher
import memory_store
import ai_analyst

# ─── Environment Variables ─────────────────────────────────────
TELEGRAM_TOKEN    = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID  = os.environ.get("TELEGRAM_CHAT_ID")
GMAIL_USER        = os.environ.get("GMAIL_USER")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
GMAIL_TO          = os.environ.get("GMAIL_TO")
WHATSAPP_PHONE    = os.environ.get("WHATSAPP_PHONE")
WHATSAPP_APIKEY   = os.environ.get("WHATSAPP_APIKEY")
DASHBOARD_URL     = os.environ.get("DASHBOARD_URL", "http://localhost:8050")

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠ Telegram not configured, skipping")
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        res = requests.post(url, json=payload)
        res.raise_for_status()
        print("✅ Telegram notification sent")
        return True
    except Exception as e:
        print(f"✗ Telegram failed: {e}")
        return False

def send_gmail(subject, html_body):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD or not GMAIL_TO:
        print("⚠ Gmail not configured, skipping")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg['Subject'] = subject
        msg['From'] = GMAIL_USER
        msg['To'] = GMAIL_TO
        
        # Create plain text version by stripping some tags (simple)
        plain_text = "Please view in an HTML compatible email client."
        
        msg.attach(MIMEText(plain_text, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        print("✅ Gmail notification sent")
        return True
    except Exception as e:
        print(f"✗ Gmail failed: {e}")
        return False

def send_whatsapp(message):
    if not WHATSAPP_PHONE or not WHATSAPP_APIKEY:
        print("⚠ WhatsApp not configured (CallMeBot), skipping")
        return False
    try:
        url = f"https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_PHONE}&text={requests.utils.quote(message)}&apikey={WHATSAPP_APIKEY}"
        res = requests.get(url)
        res.raise_for_status()
        print("✅ WhatsApp notification sent")
        return True
    except Exception as e:
        print(f"✗ WhatsApp failed: {e}")
        return False

def get_score_bar(score):
    filled = "█"
    empty = "░"
    if score >= 80: return filled * 12
    if score >= 60: return filled * 9 + empty * 3
    if score >= 40: return filled * 6 + empty * 6
    if score >= 20: return filled * 3 + empty * 9
    return filled * 1 + empty * 11

def format_telegram(report, alerts) -> str:
    date_str = datetime.now().strftime("%d %b %Y")
    sum_data = report["summary"]
    
    # Calculate avg score
    scores = [r["composite_score"] for r in report["all_results"]]
    avg_score = sum(scores) / len(scores) if scores else 0

    msg = f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"📊 <b>EQUITY BRIEFING  {date_str}</b>\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    msg += f"🌡️ <b>MARKET PULSE</b>\n"
    msg += f"🟢 Strong Buy : {sum_data['strong_buys']}    🟢 Buy    : {sum_data['buys']}\n"
    msg += f"🟡 Neutral   : {sum_data['neutrals']}    🔴 Sell   : {sum_data['sells']}\n"
    msg += f"📈 Avg Score : {avg_score:.1f}/100\n\n"
    
    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"🚀 <b>TOP PICKS TODAY</b>\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for r in report["top_momentum"][:3]:
        ai = r.get("ai_analysis", {})
        change = r['change_1d']
        msg += f"🏆 <b>{r['ticker'].split('.')[0]}</b> · ₹{r['price']} · {change:+.2f}%\n"
        msg += f"   Score  : {r['composite_score']}/100 {get_score_bar(r['composite_score'])}\n"
        msg += f"   Signal : {r['signal']}  |  RSI: {r['key_indicators']['rsi']}\n"
        msg += f"   🤖 \"{ai.get('one_liner', 'N/A')}\"\n"
        msg += f"   ⏱️  Horizon : {ai.get('time_horizon', 'N/A')}\n"
        msg += f"   🎯 Catalyst: {ai.get('key_catalyst', 'N/A')}\n\n"
        
    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"⚠️  <b>AVOID TODAY</b>\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for r in report["avoid"][:2]:
        ai = r.get("ai_analysis", {})
        msg += f"🔴 <b>{r['ticker'].split('.')[0]}</b> · ₹{r['price']} · {r['change_1d']:+.2f}%\n"
        msg += f"   Score  : {r['composite_score']}/100 {get_score_bar(r['composite_score'])}\n"
        msg += f"   🤖 \"{ai.get('one_liner', 'N/A')}\"\n"
        msg += f"   ⚡ Risk : {ai.get('key_risk', 'N/A')}\n\n"

    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"🧠 <b>AI PATTERN ALERTS</b>\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    if alerts:
        for a in alerts[:5]:
            msg += f"📌 {a['ticker']}: {a['alert']}\n"
    else:
        msg += "No significant pattern changes today\n"
        
    msg += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"🔗 <a href='{DASHBOARD_URL}'>Open Dashboard</a>\n"
    msg += f"⏰ Next update: Tomorrow 6PM IST\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    return msg

def format_email(report, alerts) -> str:
    date_str = datetime.now().strftime("%d %b %Y")
    sum_data = report["summary"]
    
    top_picks_html = ""
    for r in report["top_momentum"][:3]:
        ai = r.get("ai_analysis", {})
        top_picks_html += f"""
        <div style="background:#1e293b; border-radius:8px; padding:15px; margin-bottom:15px; border-left:4px solid #10b981;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:18px; font-weight:bold; color:#f1f5f9;">{r['ticker']}</span>
                <span style="font-size:14px; font-weight:bold; color:#10b981;">Score: {r['composite_score']}/100</span>
            </div>
            <div style="color:#94a3b8; font-size:14px; margin:5px 0;">₹{r['price']} | {r['change_1d']:+.2f}%</div>
            <div style="background:#0f172a; height:8px; border-radius:4px; margin:10px 0;">
                <div style="width:{r['composite_score']}%; height:8px; background:#10b981; border-radius:4px;"></div>
            </div>
            <div style="font-weight:bold; color:#10b981; font-size:12px; margin-bottom:10px;">{r['signal']}</div>
            <div style="color:#f1f5f9; font-style:italic; margin-bottom:10px;">🤖 "{ai.get('one_liner', 'N/A')}"</div>
            <div style="color:#94a3b8; font-size:13px; margin-bottom:10px;"><b>Reasoning:</b> {ai.get('reasoning', 'N/A')}</div>
            <div style="color:#ef4444; font-size:12px;">⚡ <b>Risk:</b> {ai.get('key_risk', 'N/A')}</div>
            <div style="color:#10b981; font-size:12px;">🎯 <b>Catalyst:</b> {ai.get('key_catalyst', 'N/A')}</div>
            <div style="color:#f59e0b; font-size:12px;">⏱️  <b>Horizon:</b> {ai.get('time_horizon', 'N/A')}</div>
        </div>
        """

    avoid_html = ""
    for r in report["avoid"][:2]:
        ai = r.get("ai_analysis", {})
        avoid_html += f"""
        <div style="background:#1e293b; border-radius:8px; padding:15px; margin-bottom:15px; border-left:4px solid #ef4444;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:18px; font-weight:bold; color:#f1f5f9;">{r['ticker']}</span>
                <span style="font-size:14px; font-weight:bold; color:#ef4444;">Score: {r['composite_score']}/100</span>
            </div>
            <div style="background:#0f172a; height:8px; border-radius:4px; margin:10px 0;">
                <div style="width:{r['composite_score']}%; height:8px; background:#ef4444; border-radius:4px;"></div>
            </div>
            <div style="color:#f1f5f9; font-style:italic; margin-bottom:5px;">🤖 "{ai.get('one_liner', 'N/A')}"</div>
            <div style="color:#ef4444; font-size:12px;">⚡ <b>Risk:</b> {ai.get('key_risk', 'N/A')}</div>
        </div>
        """

    alerts_html = ""
    if alerts:
        for a in alerts:
            alerts_html += f"<li style='margin-bottom:5px;'><b>{a['ticker']}:</b> {a['alert']}</li>"
    else:
        alerts_html = "<li>No significant pattern changes today</li>"

    table_rows = ""
    for r in report["all_results"]:
        sc = "#10b981" if "BUY" in r["signal"] else "#ef4444" if "SELL" in r["signal"] else "#f59e0b"
        table_rows += f"""
        <tr style="border-bottom:1px solid #334155;">
            <td style="padding:10px; color:#f1f5f9;">{r['ticker']}</td>
            <td style="padding:10px; color:#f1f5f9;">₹{r['price']}</td>
            <td style="padding:10px; color:{'#10b981' if r['change_1d']>=0 else '#ef4444'};">{r['change_1d']:+.2f}%</td>
            <td style="padding:10px; color:{sc}; font-weight:bold;">{r['composite_score']}</td>
            <td style="padding:10px; color:#94a3b8; font-size:11px;">{r.get('ai_analysis', {}).get('verdict', 'N/A')}</td>
        </tr>
        """

    html = f"""
    <html>
    <body style="background-color:#0f172a; font-family:Arial, sans-serif; color:#f1f5f9; padding:20px;">
        <div style="max-width:600px; margin:0 auto;">
            <div style="text-align:center; padding:20px 0; border-bottom:1px solid #334155;">
                <h1 style="margin:0; color:#10b981;">📊 EQUITY RESEARCH BRIEFING</h1>
                <div style="color:#94a3b8; font-size:14px; margin-top:5px;">{date_str} · {len(report['all_results'])} stocks analyzed</div>
            </div>
            
            <div style="padding:20px 0;">
                <h2 style="font-size:16px; color:#94a3b8; text-transform:uppercase; letter-spacing:1px;">🌡️ MARKET PULSE</h2>
                <div style="display:flex; flex-wrap:wrap; gap:10px;">
                    <span style="background:#10b98120; color:#10b981; padding:5px 10px; border-radius:4px; font-weight:bold; margin-right:10px;">🟢 Strong Buy: {sum_data['strong_buys']}</span>
                    <span style="background:#10b98115; color:#10b981; padding:5px 10px; border-radius:4px; font-weight:bold; margin-right:10px;">🟢 Buy: {sum_data['buys']}</span>
                    <span style="background:#f59e0b20; color:#f59e0b; padding:5px 10px; border-radius:4px; font-weight:bold; margin-right:10px;">🟡 Neutral: {sum_data['neutrals']}</span>
                    <span style="background:#ef444420; color:#ef4444; padding:5px 10px; border-radius:4px; font-weight:bold;">🔴 Sell: {sum_data['sells']}</span>
                </div>
            </div>

            <div style="padding:20px 0;">
                <h2 style="font-size:16px; color:#10b981; text-transform:uppercase; letter-spacing:1px; margin-bottom:15px;">🚀 TOP PICKS</h2>
                {top_picks_html}
            </div>

            <div style="padding:20px 0;">
                <h2 style="font-size:16px; color:#ef4444; text-transform:uppercase; letter-spacing:1px; margin-bottom:15px;">⚠️ AVOID TODAY</h2>
                {avoid_html}
            </div>

            <div style="padding:20px 0; background:#1e293b; border-radius:8px; padding:15px;">
                <h2 style="font-size:16px; color:#f59e0b; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;">🧠 AI PATTERN ALERTS</h2>
                <ul style="color:#f1f5f9; padding-left:20px; margin:0;">
                    {alerts_html}
                </ul>
            </div>

            <div style="padding:30px 0;">
                <h2 style="font-size:16px; color:#94a3b8; text-transform:uppercase; letter-spacing:1px; margin-bottom:15px;">📋 FULL RESULTS TABLE</h2>
                <table style="width:100%; border-collapse:collapse; font-size:13px;">
                    <thead style="background:#1e293b; color:#94a3b8;">
                        <tr>
                            <th style="padding:10px; text-align:left;">Ticker</th>
                            <th style="padding:10px; text-align:left;">Price</th>
                            <th style="padding:10px; text-align:left;">Change</th>
                            <th style="padding:10px; text-align:left;">Score</th>
                            <th style="padding:10px; text-align:left;">AI</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>

            <div style="text-align:center; padding:30px 0; color:#94a3b8; font-size:12px; border-top:1px solid #334155;">
                Generated by Equity Research Assistant Agent v3.0<br>
                <a href="{DASHBOARD_URL}" style="color:#10b981; text-decoration:none; font-weight:bold;">View Live Dashboard →</a>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def main():
    print(f"🚀 Starting L3 Agentic Daily Analysis: {datetime.now().isoformat()}")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    try:
        from config_loader import CFG
        tickers = CFG.stocks()
        
        # 1. Run basic technical analysis
        print("⚙️ Computing technical indicators...")
        report = run_daily_analysis(tickers)
        if not report: 
            print("⚠ No data generated.")
            return

        # 2. Level 3 Enrichment
        print(f"🤖 Starting L3 AI Enrichment for {len(report['all_results'])} stocks...")
        enriched_results = []
        for stock in report["all_results"]:
            ticker = stock["ticker"]
            company_name = stock.get("name", ticker)
            
            print(f"  → Enriching {ticker}...")
            
            # a. Fetch News
            news = news_fetcher.fetch_news(ticker, company_name)
            
            # b. Memory Lookup
            history = memory_store.get_history(ticker)
            streak = memory_store.get_streak(ticker)
            trend_change = memory_store.get_trend_change(ticker)
            
            # c. AI Analysis
            analysis = ai_analyst.analyze_stock(stock, news, history, streak, trend_change)
            stock["ai_analysis"] = analysis
            stock["news"] = news
            
            # d. Save to Memory
            memory_store.save_analysis(
                ticker, 
                report["date"], 
                stock["composite_score"], 
                stock["signal"],
                analysis["verdict"],
                analysis["confidence"],
                stock["price"],
                stock["key_indicators"]["rsi"],
                analysis["reasoning"]
            )
            enriched_results.append(stock)

        # 3. Finalize Enriched Report
        report["all_results"] = enriched_results
        report["top_momentum"] = [s for s in enriched_results if s["ticker"] in [x["ticker"] for x in report["top_momentum"]]]
        report["watchlist"] = [s for s in enriched_results if s["ticker"] in [x["ticker"] for x in report["watchlist"]]]
        report["avoid"] = [s for s in enriched_results if s["ticker"] in [x["ticker"] for x in report["avoid"]]]
        
        # 4. Get Watchlist Alerts
        alerts = memory_store.get_watchlist_alerts([s["ticker"] for s in enriched_results])
        
        # 5. Save Enriched JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_path = os.path.join(reports_dir, f"analysis_{timestamp}_enriched.json")
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        # Latest symlink-like save for dashboard
        with open(os.path.join(reports_dir, "latest_enriched.json"), "w") as f:
            json.dump(report, f, indent=2, default=str)
            
        print(f"✅ Enriched report saved: {output_path}")

        # 6. Send Notifications
        print("📨 Sending notifications...")
        
        tg_msg = format_telegram(report, alerts)
        send_telegram(tg_msg)
        
        email_html = format_email(report, alerts)
        subject = f"📊 {report['date']} · {report['summary']['strong_buys']} Strong Buys · Top Pick: {report['top_momentum'][0]['ticker'] if report['top_momentum'] else 'N/A'}"
        send_gmail(subject, email_html)
        
        # Plain text for WhatsApp
        wa_plain = tg_msg.replace("<b>", "").replace("</b>", "").replace("🏆", "✅").replace("🤖", "AI:").replace("⏱️", "Exp:")
        send_whatsapp(wa_plain)

    except Exception as e:
        import traceback
        print(f"❌ Daily analysis FAILED: {e}")
        traceback.print_exc()
        error_msg = f"❌ <b>Daily analysis FAILED</b> — {str(e)}"
        send_telegram(error_msg)

if __name__ == "__main__":
    main()
