import os
from supabase import create_client, Client
from config import Config

class Database:
    def __init__(self, config: Config):
        self.supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    
    def insert(self, table: str, data: dict):
        return self.supabase.table(table).insert(data).execute()
    
    def select(self, table: str, column: str, value: str):
        return self.supabase.table(table).select(column).eq(column, value).execute()
    
    def update(self, table: str, column: str, value: str, data: dict):
        return self.supabase.table(table).update(data).eq(column, value).execute()
    
    def delete(self, table: str, column: str, value: str):
        return self.supabase.table(table).delete().eq(column, value).execute()