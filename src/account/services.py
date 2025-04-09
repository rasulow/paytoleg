from twilio.rest import Client
from os import environ as env
from dotenv import load_dotenv

load_dotenv()

TWILIO_PHONE_NUMBER = env['TWILIO_PHONE_NUMBER']
TWILIO_ACCOUNT_SID = env['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = env['TWILIO_AUTH_TOKEN']

def send_sms(phone_number, code):
    message = f"Your verification code is {code}"
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )

