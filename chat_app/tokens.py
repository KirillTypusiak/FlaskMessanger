from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

SERIALIZER = URLSafeTimedSerializer(SECRET_KEY)

def generate_token(registration_id):
    TOKEN = SERIALIZER.dumps(registration_id, salt="email-verification")
    return TOKEN

def verify_token(token):
    try:
        registration_id = SERIALIZER.loads(token, salt="email-verification", max_age=900)
        return registration_id
    except SignatureExpired or BadSignature as err:
        return None
    