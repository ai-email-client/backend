from pydantic import BaseModel
from typing import List

class UserBase(BaseModel):
    username: str
    password: str
    name: str

## TODO: 
# 1. User can have many email accounts
# 2. User should have a default email account

# class UserProfile(BaseModel):
#     username: str
#     name: str
#     email_accounts: List[EmailAccountResponse] = []

# class UserResponse(BaseModel):
#     username: str
#     name: str
#     email_accounts: List[EmailAccountResponse] = []

#     class Config:
#         from_attributes = True