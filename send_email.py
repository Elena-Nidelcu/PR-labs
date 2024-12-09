import smtplib
# creates SMTP session
s = smtplib.SMTP('smtp.gmail.com', 587)
# start TLS for security
s.starttls()
sender_email = 'enidelcu@gmail.com'
password = ''  # my app password
receiver_email = 'elena.nidelcu@isa.utm.md'
# Authentication
s.login(sender_email, password)
# message to be sent
message = "Message to myself"
# sending the mail
s.sendmail(sender_email, sender_email, message)
# terminating the session
s.quit()