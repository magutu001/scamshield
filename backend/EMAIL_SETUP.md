# Email Setup Guide (Gmail)

To enable verification emails, update these two lines in `main.py`:

```python
SMTP_EMAIL    = "your_gmail@gmail.com"      # Your Gmail address
SMTP_PASSWORD = "your_app_password_here"    # Gmail App Password
```

## How to get a Gmail App Password:

1. Go to your Google Account → **Security**
2. Enable **2-Step Verification** (required)
3. Go to **Security → App passwords**
4. Select app: **Mail** → Select device: **Windows Computer**
5. Click **Generate** → Copy the 16-character password
6. Paste it as `SMTP_PASSWORD` in `main.py`

## Example:
```python
SMTP_EMAIL    = "eugine.magutu@gmail.com"
SMTP_PASSWORD = "abcd efgh ijkl mnop"   # 16-char app password (spaces are fine)
```

## Note:
If email is not configured, the system still works —
the verification code will appear in the browser as a fallback (for development/testing).
