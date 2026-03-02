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
        self.DIFY_SUMMARY = os.getenv("DIFY_SUMMARY")
        self.DIFY_WRITER = os.getenv("DIFY_WRITER")
        self.DIFY_OVERVIEW = os.getenv("DIFY_OVERVIEW")

        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.ALGORITHM = os.getenv("ALGORITHM")
