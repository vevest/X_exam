# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# import smtplib

# ##############################
# def send_verify_email(to_email, user_verification_key):
#     try:

#         # Email and password of the sender's Gmail account
#         sender_email = "vvevest@gmail.com"
#         password = "sayq hyqz sppy mhiv" 

#         # Receiver email address
#         receiver_email = "vvevest@gmail.com"
        
#         # Create the email message
#         message = MIMEMultipart()
#         message["From"] = "My company name"
#         message["To"] = receiver_email
#         message["Subject"] = "Please verify your account"

#         # Body of the email
#         body = f"""To verify your account, please <a href="http://127.0.0.1/verify/{user_verification_key}">click here</a>"""
#         message.attach(MIMEText(body, "html"))

#         # Connect to Gmail's SMTP server and send the email
#         with smtplib.SMTP("smtp.gmail.com", 587) as server:
#             server.starttls()  # Upgrade the connection to secure
#             server.login(sender_email, password)
#             server.sendmail(sender_email, receiver_email, message.as_string())
#         print("Email sent successfully!")

#         return "email sent"
       
#     except Exception as ex:
#         raise_custom_exception("cannot send email", 500)
#     finally:
#         pass