import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

mcp = FastMCP("SMTP Mail Tools")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)

ALLOWLIST = set(
    e.strip().lower()
    for e in (os.getenv("NEWSLETTER_ALLOWLIST", "")).split(",")
    if e.strip()
)

@mcp.tool()
def send_email(recipient: str, subject: str, body_text: str) -> dict:

    rcp = recipient.strip().lower()

    if ALLOWLIST and rcp not in ALLOWLIST:
        return {"ok": False, "error": f"recipient not in allowlist: {recipient}"}

    msg = EmailMessage()
    msg["From"] = SMTP_FROM
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body_text)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)

        return {"ok": True}

    except Exception as e:
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    mcp.run()