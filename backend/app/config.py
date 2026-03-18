import os
from dotenv import load_dotenv

# Load .env file from backend/ folder
load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH      = os.path.join(BASE_DIR, "scam_detection.db")
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))

# ── Admin credentials ──────────────────────────────────────────────────────────
ADMIN_EMAIL    = os.getenv("ADMIN_EMAIL", "admin@scamdetect.ke")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_TOKEN    = os.getenv("ADMIN_TOKEN", "scamshield-admin-token-2025")

# ── Email — loaded from .env file ──────────────────────────────────────────────
SMTP_EMAIL    = os.getenv("SMTP_EMAIL", "your_gmail@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_app_password")
SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
