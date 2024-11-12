# -*- coding: utf-8 -*-
import smtplib
import ssl
import os

# import mime type to send vnese email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send(receiver, msg):
    host = 'smtp.gmail.com'
    port = 465

    username = 'long.ezmar.001@gmail.com'
    password= os.getenv('PASSWORD')

    subject_line, body = msg.split('\n', 1)
    subject = subject_line.replace("Subject: ", "").strip()

    message = MIMEMultipart()
    message['From'] = username
    message['To'] = receiver
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain', 'utf-8'))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message.as_string())