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
        
        self.FRONTEND_API_URL = os.getenv("FRONTEND_API_URL")

        self.SUPABASE_URL = os.getenv("SUPABASE_URL")
        self.SUPABASE_KEY = os.getenv("SUPABASE_KEY")

        self.DIFY_URL = os.getenv("DIFY_URL")
        self.DIFY_API_KEY = os.getenv("DIFY_API_KEY")

        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.ALGORITHM = os.getenv("ALGORITHM")
