# 🏥 Pharmacy Ordering System — Setup Guide

## 📁 Project Structure
```
pharmacy-bot/
├── bot.py              ← Telegram Bot
├── main.py             ← FastAPI Backend API
├── database.py         ← Database connection
├── models.py           ← Database tables
├── schemas.py          ← Data validation
├── requirements.txt
├── .env.example        ← Copy to .env and fill in
└── webapp/
    └── index.html      ← Doctor-facing Web App
```

---

## 🚀 Step-by-Step Setup

### Step 1 — Create Telegram Bot
1. Open Telegram → search **@BotFather**
2. Send `/newbot`
3. Follow instructions, get your **BOT_TOKEN**
4. Send `/setmenubutton` to set the web app button (optional)

### Step 2 — Get Pharmacy Chat ID
1. Add **@userinfobot** to your pharmacy Telegram group (or DM it)
2. It will reply with your Chat ID
3. For a group: add the bot to the group, it shows the group's ID

### Step 3 — Host the Web App
Option A — **GitHub Pages** (free):
1. Push `webapp/index.html` to a GitHub repo
2. Enable GitHub Pages in repo Settings
3. Your URL will be: `https://yourusername.github.io/repo-name/`

Option B — **Netlify** (free, drag & drop):
1. Go to netlify.com
2. Drag the `webapp/` folder
3. Get instant URL

### Step 4 — Configure Environment
```bash
cp .env.example .env
# Edit .env with your values
```

### Step 5 — Install & Run Backend
```bash
pip install -r requirements.txt

# Start API server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 6 — Update Web App URL
In `webapp/index.html`, line with `const API = ...`:
```js
const API = "https://your-server-ip:8000";
// OR if using a domain:
const API = "https://api.yourdomain.com";
```

### Step 7 — Run the Bot
```bash
python bot.py
```

---

## 📦 Add Medicines (Pharmacy Admin)
Use the API directly to add medicines:

```bash
curl -X POST http://localhost:8000/medicines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Paracetamol 500mg",
    "category": "Pain Relief",
    "price": 25.00,
    "profit_margin": 15.0,
    "stock": 500,
    "unit": "strip"
  }'
```

Or open `http://localhost:8000/docs` for the interactive API explorer.

---

## 🔔 How Notifications Work
1. Doctor places order via Web App
2. Backend saves order to database
3. Backend sends Telegram message to PHARMACY_CHAT_ID instantly
4. Message includes: Doctor name, phone, all items, quantities, total

---

## 📊 Check Orders
```
GET /orders              → All orders
GET /orders?status=pending → Pending orders only
GET /orders/{doctor_id}  → Doctor's orders
PUT /orders/{id}/status  → Update status
```

---

## 🌐 Production Deployment (VPS)
```bash
# Install nginx, certbot for HTTPS
# Use systemd or supervisor to keep bot + API running
# Use PostgreSQL instead of SQLite for production
```

---

## 💬 Support
Built with: FastAPI + python-telegram-bot + SQLite/PostgreSQL
