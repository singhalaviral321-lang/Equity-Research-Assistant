# 🚀 DEPLOY NOW: Equity Research Assistant

Follow this guide to get your stock research assistant running in the cloud for free.

---

## 🛠️ PART A — One-Time Setup

### A1. Install Python on Windows
1. Go to [python.org](https://www.python.org/downloads/) and download the latest version.
2. **IMPORTANT:** While installing, check the box that says **"Add Python to PATH"**.
3. Open a terminal (Type `cmd` in Start) and type `python --version` to verify.

### A2. Install Git on Windows
1. Download Git from [git-scm.com](https://git-scm.com/download/win).
2. Install with default settings.

### A3. Create a GitHub Repo
1. Sign in to [GitHub](https://github.com/).
2. Click **New** to create a repository named `stock-research-assistant`.
3. Keep it **Public** (or Private if you prefer).

### A4. Push Code to GitHub
Open your project folder in CMD or PowerShell and run:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/stock-research-assistant.git
git push -u origin main
```
*(Replace YOUR_USERNAME with your actual GitHub name)*

### A5. Set up Railway.app (For Dashboard)
1. Go to [Railway.app](https://railway.app/) and sign in with GitHub.
2. Click **New Project** > **Deploy from GitHub repo**.
3. Select your repo.
4. Go to the **Variables** tab and add all variables from `.env.template`.

### A6. Set up GitHub Secrets (For Daily Automation)
1. In your GitHub repo, go to **Settings** > **Secrets and variables** > **Actions**.
2. Add these **Repository secrets**:
   - `TELEGRAM_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `GMAIL_USER`
   - `GMAIL_APP_PASSWORD`
   - `GMAIL_TO`
   - `WHATSAPP_PHONE`
   - `WHATSAPP_APIKEY`
   - `DASHBOARD_URL` (Your Railway URL)

### A7. Set up Telegram Bot
1. Message [@BotFather](https://t.me/botfather) and click `/newbot`.
2. Follow steps to get your **Bot Token**.
3. Message [@userinfobot](https://t.me/userinfobot) to get your **Chat ID**.

### A8. Set up Gmail App Password
1. Go to [Google Account Settings](https://myaccount.google.com/security).
2. Enable **2-Step Verification**.
3. Search for **"App Passwords"** at the top.
4. Create one for "Mail" and "Windows Computer". Copy the 16-character code.

### A9. Set up WhatsApp (CallMeBot)
1. Add `+34 644 66 21 54` to your contacts.
2. Send message: `I allow callmebot to send me messages`
3. You will receive an **API Key**.

---

## 📅 PART B — Daily Operation

### B1. Automated Trading View
At **6:00 PM IST (12:30 PM UTC)** every weekday, GitHub will automatically:
- Fetch latest stock data.
- Run the analysis engine.
- Save a JSON report to your repo.
- Send you notifications on Telegram, Email, and WhatsApp.

### B2. Manual Trigger
1. Go to your GitHub repo.
2. Click **Actions** tab.
3. Select **Daily Stock Analysis** on the left.
4. Click **Run workflow** > **Run workflow** (button).

### B3. Changing Stock List
1. Edit `config.json` directly on GitHub or locally.
2. Add tickers like `RELIANCE.NS` (NSE) or `AAPL` (US).
3. Commit and push changes.

---

## 🔍 PART C — Troubleshooting

- **"No reports found" on Dashboard**: This means the first analysis hasn't run yet. Trigger it manually using Part B2.
- **GitHub Actions failed**: Click on the red "X" in the Actions tab to see the error logs.
- **Telegram not receiving**: Check if your bot is started and Chat ID is correct.
- **Old data on Dashboard**: Railway reads from the `reports/` folder in your repo. Ensure GitHub Actions is successfully pushing files back.
