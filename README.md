# 🛡 ScamShield — Job Scam Detection System

**Technical University of Mombasa | BSIT/558J/2021 | Eugine Nyansimera Magutu**

A web-based system that detects fraudulent job advertisements using rule-based text analysis, domain verification (WHOIS, SSL, domain age), and weighted risk scoring.

---

## 📸 Features

| Feature | Description |
|---|---|
| 🔍 Text Analysis | Regex-based detection of 10+ scam indicator categories |
| 🌐 Domain Check | SSL certificate, WHOIS, and domain age verification |
| 📊 Risk Scoring | Weighted cumulative score → Safe / Caution / High Risk verdict |
| 📋 History | Full log of all analyzed advertisements |
| ⚙️ Admin Panel | Add, edit, enable/disable detection rules |
| 📱 Mobile-Friendly | Responsive design for smartphone use |

---

## 🚀 Quick Start

### Windows
```bat
double-click start.bat
```

### Mac / Linux
```bash
chmod +x start.sh
./start.sh
```

Then open **http://localhost:8000** in your browser.

---

## 🗂 Project Structure

```
job-scam-detector/
├── backend/
│   ├── main.py              ← FastAPI app, all endpoints & logic
│   ├── requirements.txt     ← Python dependencies
│   └── scam_detection.db    ← SQLite3 database (auto-created)
├── frontend/
│   ├── index.html           ← Single-page app
│   └── static/
│       ├── css/style.css    ← All styles
│       └── js/app.js        ← All frontend logic
├── .vscode/
│   ├── launch.json          ← Run config (F5 to start)
│   ├── settings.json
│   └── extensions.json
├── start.bat                ← Windows launcher
├── start.sh                 ← Mac/Linux launcher
└── README.md
```

---

## 🛠 Manual Setup (VS Code)

1. **Open folder in VS Code:**
   ```
   File → Open Folder → select job-scam-detector/
   ```

2. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Run with VS Code debugger:**
   - Press **F5** or go to Run → Start Debugging
   - Ensure "Run ScamShield Backend" is selected

4. **Or run from terminal:**
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

5. Open **http://localhost:8000**

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/analyze` | Analyze a job advertisement |
| GET | `/api/history` | Get analysis history |
| GET | `/api/stats` | Dashboard statistics |
| GET | `/api/rules` | List all detection rules |
| POST | `/api/rules` | Add a new rule |
| PUT | `/api/rules/{id}` | Update a rule |
| DELETE | `/api/rules/{id}` | Delete a rule |

---

## 📊 Risk Score Interpretation

| Score | Verdict | Meaning |
|---|---|---|
| 0–29 | ✅ LIKELY SAFE | No major indicators found |
| 30–59 | ⚠️ NEEDS CAUTION | Some suspicious characteristics |
| 60+ | 🚨 HIGH RISK | Multiple strong scam indicators |

---

## 🧪 Technology Stack

- **Backend:** Python 3.9+, FastAPI, SQLite3, python-whois
- **Frontend:** Vanilla HTML/CSS/JavaScript (no frameworks)
- **Fonts:** Syne + DM Sans (Google Fonts)

---

## 👤 Default Admin Credentials

| Email | Password |
|---|---|
| admin@scamdetect.ke | admin123 |

---

## 📚 Academic Reference

This system was developed as a Final Year Research Project for the Bachelor of Science in Information Technology at the Technical University of Mombasa, December 2025.

**Supervisor:** Mr. Gavuna
