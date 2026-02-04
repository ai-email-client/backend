from supabase import create_client, Client
from config import Config

class SupabaseDB:
    def __init__(self, config: Config):
        self.config = config
        self.supabase: Client = create_client(self.config.SUPABASE_URL, self.config.SUPABASE_KEY)
