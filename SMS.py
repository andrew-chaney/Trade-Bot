import smtplib
from email.message import EmailMessage

def text(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to

    user = 'ENTER VALID EMAIL HERE'
    msg['from'] = user
    passw = 'ENTER PASSWORD HERE'

    # For gmail
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(user, passw)
    server.send_message(msg)
    server.quit()
