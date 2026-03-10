import os
import json
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from indicator_engine import run_daily_analysis

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

def send_gmail(subject, body):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD or not GMAIL_TO:
        print("⚠ Gmail not configured, skipping")
        return False
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = GMAIL_USER
        msg['To'] = GMAIL_TO

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
        # CallMeBot WhatsApp API
        url = f"https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_PHONE}&text={requests.utils.quote(message)}&apikey={WHATSAPP_APIKEY}"
        res = requests.get(url)
        res.raise_for_status()
        print("✅ WhatsApp notification sent")
        return True
    except Exception as e:
        print(f"✗ WhatsApp failed: {e}")
        return False

def format_message(report):
    date_str = datetime.now().strftime("%d %b %Y")
    sum = report["summary"]
    
    msg = f"📊 <b>Daily Equity Briefing — {date_str}</b>\n"
    msg += "══════════════════════\n"
    msg += f"🟢 Strong Buy: {sum['strong_buys']}  |  🟢 Buy: {sum['buys']}\n"
    msg += f"🟡 Neutral: {sum['neutrals']}     |  🔴 Sell: {sum['sells']}\n\n"
    
    if report["top_momentum"]:
        msg += "🚀 <b>Top Picks:</b>\n"
        for r in report["top_momentum"][:2]:
            msg += f"✅ {r['ticker']:10s} Score:{int(r['composite_score'])}  ▲{r['change_1d']:+.1f}%\n"
        msg += "\n"
        
    if report["avoid"]:
        msg += "⚠️ <b>Avoid:</b>\n"
        for r in report["avoid"][:1]:
            msg += f"🔴 {r['ticker']:10s} Score:{int(r['composite_score'])}  ▼{r['change_1d']:+.1f}%\n"
        msg += "\n"
        
    msg += f"🔗 <a href='{DASHBOARD_URL}'>Open Dashboard</a>"
    return msg

def main():
    print(f"🚀 Starting daily analysis: {datetime.now().isoformat()}")
    
    # 1. Path fix: Ensure reports directory exists relative to script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    reports_dir = os.path.join(base_dir, "reports")
    
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
        
    try:
        # 2. Run analysis
        # Using tickers from config by default as requested in Task 8/4
        # But indicator_engine.py main block reads from stocks.txt or args
        # We'll let indicator_engine handle it
        import sys
        from config_loader import CFG
        tickers = CFG.stocks()
        if not tickers:
            print("⚠ No tickers found in config, using defaults from indicator_engine")
            tickers = None # This will trigger defaults in run_daily_analysis if modified correctly

        report = run_daily_analysis(tickers)
        
        # 3. Save report locally
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_path = os.path.join(reports_dir, f"analysis_{timestamp}.json")
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"✅ Report saved to: {os.path.abspath(output_path)}")
        
        # 4. Send Notifications
        msg_html = format_message(report)
        msg_plain = msg_html.replace("<b>", "").replace("</b>", "").replace("<a>", "").replace("</a>", "").replace("href=", "").replace("'", "")
        
        send_telegram(msg_html)
        
        date_str = datetime.now().strftime("%d %b %Y")
        sum_data = report["summary"]
        subject = f"📊 Daily Equity Briefing — {date_str} | {sum_data['strong_buys']} Strong Buys"
        send_gmail(subject, msg_plain)
        
        send_whatsapp(msg_plain)
        
    except Exception as e:
        print(f"❌ Daily analysis FAILED: {e}")
        error_msg = "❌ <b>Daily analysis FAILED</b> — check GitHub Actions logs"
        send_telegram(error_msg)
        raise e

if __name__ == "__main__":
    main()
