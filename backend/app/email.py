import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import SMTP_EMAIL, SMTP_PASSWORD, SMTP_HOST, SMTP_PORT


def send_verification_email(to_email: str, name: str, code: str) -> bool:
    """Send a verification or password reset code to the user's email."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Your ScamShield Verification Code: {code}"
        msg["From"]    = SMTP_EMAIL
        msg["To"]      = to_email

        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;
                    background:#0a0c10;color:#f0f2f5;padding:36px;border-radius:16px;">
          <div style="text-align:center;margin-bottom:28px;">
            <span style="font-size:36px;">🛡</span>
            <h2 style="color:#00e5a0;margin:8px 0 4px;">ScamShield Kenya</h2>
            <p style="color:#505866;font-size:13px;margin:0;">Job Scam Detection System</p>
          </div>
          <p style="color:#8a92a0;">Hi <strong style="color:#f0f2f5;">{name}</strong>,</p>
          <p style="color:#8a92a0;">Use the verification code below:</p>
          <div style="background:#111318;border:1px solid rgba(0,229,160,0.2);
                      border-radius:12px;padding:28px;text-align:center;margin:24px 0;">
            <div style="font-size:42px;font-weight:800;letter-spacing:12px;color:#00e5a0;">
              {code}
            </div>
            <p style="color:#505866;font-size:12px;margin:12px 0 0;">Valid for 10 minutes</p>
          </div>
          <p style="color:#505866;font-size:12px;">
            If you did not request this, please ignore this email.
          </p>
        </div>
        """
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        return True

    except Exception as e:
        print(f"Email error: {e}")
        return False
