import smtplib
from email.mime.text import MIMEText

sender_email = "timmarticio@gmail.com"
receiver_email = "marcoteodorojavier@gmail.com"
app_password = "vscl nbmt jtqi hrto"

msg = MIMEText("Hello from Flask!")
msg["Subject"] = "Test Email"
msg["From"] = sender_email
msg["To"] = receiver_email

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(sender_email, app_password)
    server.send_message(msg)