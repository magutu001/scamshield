# 🛡 ScamShield — Job Scam Detection System

A web-based system that analyzes job advertisements to detect potential scams using regex pattern matching, domain verification, and risk scoring.

Built as an undergraduate project at **Technical University of Mombasa (TUM)**.

---

## Features

- **Automated scam detection** using 10+ regex-based detection rules
- **Domain verification** — SSL certificate check and WHOIS domain age lookup
- **Risk scoring** — verdicts of High Risk, Needs Caution, or Likely Safe
- **User authentication** — register, login, email verification, password reset
- **Scan history** — each user sees their own scan records
- **Admin panel** — manage detection rules, view all users and scan history
- **Mobile responsive** — works on phones and tablets

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Database | SQLite |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Email | Gmail SMTP / python-dotenv |
| Domain Check | python-whois, SSL socket |

---

## Project Structure

```
job-scam-detector/
├── backend/
│   ├── main.py                  # App entry point
│   ├── requirements.txt
│   ├── .env.example             # Email credentials template
│   └── app/
│       ├── config.py            # Configuration settings
│       ├── models.py            # Request/response models
│       ├── database.py          # DB connection and initialization
│       ├── auth.py              # Authentication helpers
│       ├── email.py             # Email sending
│       ├── detection.py         # Scam analysis and scoring
│       └── routes/
│           ├── auth_routes.py      # Register, login, password reset
│           ├── analysis_routes.py  # Analyze, history, stats
│           └── admin_routes.py     # Admin — rules and users
└── frontend/
    ├── index.html
    ├── admin-login.html
    ├── admin-panel.html
    └── static/
        ├── css/style.css
        └── js/app.js
```

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/magutu001/scamshield.git
cd scamshield
```

**2. Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

**3. Configure email credentials**

Copy `.env.example` to `.env` in the `backend/` folder and fill in your credentials:
```
SMTP_EMAIL=your_gmail@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

**4. Run the server**
```bash
python -m uvicorn main:app --reload --port 8000
```

**5. Open in browser**
```
http://localhost:8000
```

---

## Admin Access

The admin panel is accessible at:
```
http://localhost:8000/admin-login
```

Admin credentials are configured in `backend/app/config.py`.

---

## How It Works

1. User pastes a job advertisement into the system
2. The text is scanned against 10 regex detection rules
3. Each matched rule adds a weighted score
4. The domain is verified via SSL check and WHOIS lookup
5. Domain age and SSL status add additional penalty scores
6. Final verdict is calculated:
   - **Score ≥ 60** → HIGH RISK 🚨
   - **Score 30–59** → NEEDS CAUTION ⚠️
   - **Score < 30** → LIKELY SAFE ✅

---

## Author

**Eugine Nyansimera Magutu**
BSc Information Technology
Technical University of Mombasa
