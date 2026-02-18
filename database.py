from typing import List, Dict, Any, Optional
from config import Config
from supabase import Client,create_client

class SupabaseDB:
    def __init__(self, config: Config, client: Optional[Client] = None):
        self.config = config
        
        if client:
            self.supabase = client
        else:
            self.supabase = create_client(
                config.SUPABASE_URL,
                config.SUPABASE_KEY
            )

    def select(self, table: str, columns: str = "*", eq: Optional[Dict[str, Any]] = None) -> List[Dict]:
        try:
            query = self.supabase.table(table).select(columns)
            
            if eq:
                for key, value in eq.items():
                    query = query.eq(key, value)
            
            response = query.execute()
            return response.data
        except Exception as e:
            raise Exception(f"Select Error ({table}): {str(e)}")

    def insert(self, table: str, data: Dict[str, Any] | List[Dict[str, Any]]) -> List[Dict]:

        try:
            response = self.supabase.table(table).insert(data).execute()
            return response.data
        except Exception as e:
            raise Exception(f"Insert Error ({table}): {str(e)}")

    def update(self, table: str, data: Dict[str, Any], eq: Dict[str, Any]) -> List[Dict]:

        try:
            query = self.supabase.table(table).update(data)
            
            for key, value in eq.items():
                query = query.eq(key, value)
                
            response = query.execute()
            return response.data
        except Exception as e:
            raise Exception(f"Update Error ({table}): {str(e)}")

    def upsert(self, table: str, data: Dict[str, Any], on_conflict: Optional[str] = None) -> List[Dict]:

        try:
            opts = {'on_conflict': on_conflict} if on_conflict else {}
            
            response = self.supabase.table(table).upsert(data, **opts).execute()
            return response.data
        except Exception as e:
            raise Exception(f"Upsert Error ({table}): {str(e)}")
            
    def delete(self, table: str, filters: Dict[str, Any]) -> List[Dict]:
        try:
            query = self.supabase.table(table).delete()
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.execute()
            return response.data
        except Exception as e:
            raise Exception(f"Delete Error ({table}): {str(e)}")
        
def get_db_session(config: Config) -> SupabaseDB:
    return SupabaseDB(config)