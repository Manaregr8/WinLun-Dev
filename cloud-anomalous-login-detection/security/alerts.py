import smtplib 
from email.mime.text import MIMEText

smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_user = "<your_ip>"
smtp_pass = "<your-password>" # change this later as this should be kept private

alert_receiver = "lakshyajuneja925@gmail.com"

def send_email_alert(result: dict):
    subject = f"[ALERT] High Risk Login for User {result['user_id']}"
    body = f"""
    ---> High Risk Login Detected <---

    User: {result['user_id']}
    Score: {result['risk_score']}
    Reasons: {', '.join(result['reasons'])}
    Location: {result['geo'].get('city')}, {result['geo'].get('country')}
    """

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = alert_receiver

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)