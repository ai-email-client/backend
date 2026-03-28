from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from typing import List

Base = declarative_base()

class GoogleAccount(Base):
    __tablename__ = "google_accounts"

    email_address = Column(String, nullable=False)
    credentials = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SourceEmail(Base):
    __tablename__ = "source_emails"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Text, unique=True, index=True)
    plain_text = Column(Text)
    email_tag = Column(List(Text))
    status = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    


    
    
