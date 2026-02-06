from supabase import create_client, Client
from config import Config

class SupabaseDB:
    def __init__(self, config: Config):
        self.config = config
        self.supabase: Client = create_client(self.config.SUPABASE_URL, self.config.SUPABASE_KEY)
        
    def select(self, table: str, columns: str, filters: dict):
        try:
            query = self.supabase.table(table).select(columns)
            for key, value in filters.items():
                query = query.eq(key, value)
            response = query.execute()
            return response
        except Exception as e:
            raise Exception(f"Error selecting from {table}: {str(e)}")

    def insert(self, table: str, data: dict):
        try:
            response = self.supabase.table(table).insert(data).execute()
            return response
        except Exception as e:
            raise Exception(f"Error inserting into {table}: {str(e)}")
        
    def update(self, table: str, data: dict, filters: dict):
        try:
            query = self.supabase.table(table)
            for key, value in filters.items():
                query = query.eq(key, value)
            response = query.update(data).execute()
            return response
        except Exception as e:
            raise Exception(f"Error updating {table}: {str(e)}")
    
    def upsert(self, table: str, data: dict, conflict_target: str):
        try:
            response = self.supabase.table(table).upsert(data, on_conflict=conflict_target).execute()
            return response
        except Exception as e:
            raise Exception(f"Error upserting into {table}: {str(e)}")