from flask import request, make_response, render_template
import mysql.connector
import re 
import dictionary
import json

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from functools import wraps

from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

UPLOAD_ITEM_FOLDER = './images'

google_spread_sheet_key = '1r44v6UJ3wZAcq84AFKMfXUym4Vx-OGIKECmAUAuPDac'

allowed_languages = ["english", "danish", "spanish"]
default_language = "english"

##############################
def db():
    try:
        db = mysql.connector.connect(
            host = "mariadb",
            user = "root",  
            password = "password",
            database = "x"
        )
        cursor = db.cursor(dictionary=True)
        return db, cursor
    except Exception as e:
        print(e, flush=True)
        raise Exception("Twitter exception - Database under maintenance", 500)


##############################
def no_cache(view):
    @wraps(view)
    def no_cache_view(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return no_cache_view

def categorize_input(lan="english"):
    
    if lan not in allowed_languages:
        lan = "english"

    user_input = request.form.get("user_input", "").strip()
    if not user_input:
        raise Exception(lans("invalid_credentials"), 400)

    # hvis det matcher email regex -> valider som email
    if re.match(REGEX_EMAIL, user_input): 
        # validate_user_email_input bør tage input som arg
        return validate_user_email_input(user_input, lan)

    # ellers valider som username
    if re.match(REGEX_USER_USERNAME,user_input): 
        return validate_username_input(user_input, lan)

def validate_user_email_input(email, lan="english"):
    if lan not in allowed_languages:
        lan = "english"
    email = email.strip().lower()   # normaliser email til lowercase
    if not re.match(REGEX_EMAIL, email):
        raise Exception(lans("invalid_credentials"), 400)
    return email

def validate_username_input(username, lan="english"):
    if lan not in allowed_languages:
        lan = "english"
    username = username.strip()
    error = f"{lans('username')} min {USER_USERNAME_MIN} max {USER_USERNAME_MAX} {lans('characters')}"
    if len(username) < USER_USERNAME_MIN or len(username) > USER_USERNAME_MAX:
        raise Exception(error, 400)
    # evt. ekstra regex checks her hvis du ønsker (fx kun alfanumeriske)
    return username


##############################
REGEX_EMAIL = "^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
def validate_user_email(lan = "english"):
    if lan not in allowed_languages: lan = "english"
    user_email = request.form.get("user_email", "").strip()
    if not re.match(REGEX_EMAIL, user_email): raise Exception(lans("invalid_credentials"), 400)
    #this says if the email is invalid get the error message from the invalid email
    return user_email


##############################
USER_USERNAME_MIN = 2
USER_USERNAME_MAX = 20
REGEX_USER_USERNAME = f"^.{{{USER_USERNAME_MIN},{USER_USERNAME_MAX}}}$"
def validate_user_username(lan = "english"):
    if lan not in allowed_languages: lan = "english"
    user_username = request.form.get("user_username", "").strip()
    error = f"{lans('username')} min {USER_USERNAME_MIN} max {USER_USERNAME_MAX} {lans('characters')}"
    if len(user_username) < USER_USERNAME_MIN: raise Exception(error, 400)
    if len(user_username) > USER_USERNAME_MAX: raise Exception(error, 400)
    if not re.match(REGEX_USER_USERNAME, user_username): raise Exception(lans("invalid_credentials"), 400)
    return user_username



##############################
USER_FIRST_NAME_MIN = 2
USER_FIRST_NAME_MAX = 20
REGEX_USER_FIRST_NAME = f"^.{{{USER_FIRST_NAME_MIN},{USER_FIRST_NAME_MAX}}}$"
def validate_user_first_name(lan = "english"):
    if lan not in allowed_languages: lan = "english"
    user_first_name = request.form.get("user_first_name", "").strip()
    error = f"{lans('first_name')} min {USER_FIRST_NAME_MIN} max {USER_FIRST_NAME_MAX} {lans('characters')}"
    if not re.match(REGEX_USER_FIRST_NAME, user_first_name): raise Exception(error, 400)
    return user_first_name


##############################
USER_PASSWORD_MIN = 6
USER_PASSWORD_MAX = 50
REGEX_USER_PASSWORD = f"^.{{{USER_PASSWORD_MIN},{USER_PASSWORD_MAX}}}$"
def validate_user_password(lan = "english"):
    if lan not in allowed_languages: lan = "english"
    user_password = request.form.get("user_password", "").strip()
    if not re.match(REGEX_USER_PASSWORD, user_password): raise Exception(lans("invalid_credentials"), 400)
    return user_password




##############################
def validate_user_password_confirm():
    user_password = request.form.get("user_password_confirm", "").strip()
    if not re.match(REGEX_USER_PASSWORD, user_password): raise Exception("Twitter exception - Invalid confirm password", 400)
    return user_password


##############################
REGEX_UUID4 = "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
def validate_uuid4(uuid4 = ""):
    if not uuid4:
        uuid4 = request.values.get("uuid4", "").strip()
    if not re.match(REGEX_UUID4, uuid4): raise Exception("Twitter exception - Invalid uuid4", 400)
    return uuid4


##############################
REGEX_UUID4_WITHOUT_DASHES = "^[0-9a-f]{8}[0-9a-f]{4}4[0-9a-f]{3}[89ab][0-9a-f]{3}[0-9a-f]{12}$"
def validate_uuid4_without_dashes(uuid4 = ""):
    error = "Invalid uuid4 without dashes"
    if not uuid4: raise Exception(error, 400)
    uuid4 = uuid4.strip()
    if not re.match(REGEX_UUID4_WITHOUT_DASHES, uuid4): raise Exception(error, 400)
    return uuid4

##############################
POST_MIN_LEN = 2
POST_MAX_LEN = 250
REGEX_POST = f"^.{{{POST_MIN_LEN},{POST_MAX_LEN}}}$"
def validate_post(post = ""):
    post = post.strip()
    if not re.match(REGEX_POST, post): raise Exception("x-error post", 400)
    return post


##############################
def send_email(to_email, subject, template):
    try:
        # Create a gmail fullflaskdemomail
        # Enable (turn on) 2 step verification/factor in the google account manager
        # Visit: https://myaccount.google.com/apppasswords
        # Copy the key : pdru ctfd jdhk xxci

        # Email and password of the sender's Gmail account
        sender_email = "Vvevest@gmail.com"
        password = "sayq hyqz sppy mhiv" 

        # Receiver email address
        receiver_email = to_email
        
        # Create the email message
        message = MIMEMultipart()
        message["From"] = "X clone"
        message["To"] = to_email
        message["Subject"] = subject

        # Body of the email
        message.attach(MIMEText(template, "html"))

        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        ic("Email sent successfully!")

        return "email sent"
       
    except Exception as ex:
        ic(ex)
        raise Exception("cannot send email", 500)
    finally:
        pass

def lans(key):
    with open("dictionary.json", 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data[key][default_language]