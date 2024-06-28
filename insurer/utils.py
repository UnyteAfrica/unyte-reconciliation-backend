import pyotp
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def generate_otp() -> str:
    totp = pyotp.TOTP(pyotp.random_base32(), interval=60)
    otp = totp.now()

    return otp
