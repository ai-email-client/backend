from pydantic import BaseModel

class EmailSchema(BaseModel):
    subject: str
    body: str
    sender: str
    receiver: str
    
