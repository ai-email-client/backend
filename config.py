import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        self.GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
        self.GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
        self.GOOGLE_AUTH_URI = os.getenv("GOOGLE_AUTH_URI")
        self.GOOGLE_TOKEN_URI = os.getenv("GOOGLE_TOKEN_URI")
        
        self.DATABASE_URL = os.getenv("DATABASE_URL")
