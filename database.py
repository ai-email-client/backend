from typing import List, Dict, Any, Optional

from rich import table
from config import Config
from supabase import Client,create_client

class SupabaseDB:
    def __init__(self, config: Config, client: Optional[Client] = None):
        self.config = config
        if client:
            self.supabase = client
        elif config.SUPABASE_KEY and config.SUPABASE_URL:
            self.supabase = create_client(
                config.SUPABASE_URL,
                config.SUPABASE_KEY
            )
        else:
            self.supabase = None
        
    def select(
        self, 
        table: str, 
        columns: str = "*", 
        eq: Optional[Dict[str, Any]] = None,
        contains: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        if not self.supabase:
            raise Exception("Supabase client is not initialized")
        try:
            query = self.supabase.table(table).select(columns)
            
            if eq:
                for key, value in eq.items():
                    query = query.eq(key, value)
                    
            if contains:
                for key, value in contains.items():
                    query = query.contains(key, value)
            
            response = query.execute()
            return response.data
        except Exception as e:
            raise Exception(f"Select Error ({table}): {str(e)}")

    def insert(self, table: str, data: Dict[str, Any] | List[Dict[str, Any]]) -> List[Any]:
        if not self.supabase:
            raise Exception("Supabase client is not initialized")
        try:
            response = self.supabase.table(table).insert(data).execute()
            return response.data
        except Exception as e:
            raise Exception(f"Insert Error ({table}): {str(e)}")

    def update(self, table: str, data: Dict[str, Any], eq: Dict[str, Any]) -> List[Any]:
        if not self.supabase:
            raise Exception("Supabase client is not initialized")
        try:
            query = self.supabase.table(table).update(data)
            
            for key, value in eq.items():
                query = query.eq(key, value)
                
            response = query.execute()
            return response.data
        except Exception as e:
            raise Exception(f"Update Error ({table}): {str(e)}")

    def upsert(self, table: str, data: Dict[str, Any], on_conflict: Optional[str] = None) -> List[Any]:
        if not self.supabase:
            raise Exception("Supabase client is not initialized")
        try:
            if on_conflict is None:
                response = self.supabase.table(table).upsert(
                    data
                ).execute()
            else:
                response = self.supabase.table(table).upsert(
                    data, 
                    on_conflict=on_conflict
                ).execute()
            return response.data
        except Exception as e:
            raise Exception(f"Upsert Error ({table}): {str(e)}")
            
    def delete(self, table: str, filters: Dict[str, Any]) -> List[Any]:
        if not self.supabase:
            raise Exception("Supabase client is not initialized")
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