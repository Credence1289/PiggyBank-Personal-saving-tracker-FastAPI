from pydantic import BaseModel,EmailStr
from typing import Optional
from datetime import datetime

class User(BaseModel):
    user_id: Optional[int] = None
    name: str
    mobile_no: str
    email: EmailStr
    password: str | None = None

class UserCreate(BaseModel):
    name:str
    email:EmailStr
    mobile_no:str
    password:str

class PiggyBank(BaseModel):
    piggybank_id: Optional[int] = None
    user_id: int
    passwordpb:str | None = None
    name:str
    target_amount: float
    balance: float = 0.0
    is_target_active: bool = True

class PiggyBankCreate(BaseModel):
    name:str
    target_amount:float
    passwordpb:str

class Transaction(BaseModel):
    transaction_id: Optional[int] = None
    piggybank_id: int
    type: str  # "deposit" or "withdraw"
    amount: float
    time_stamp : Optional[datetime] = None



class Token(BaseModel):
    access_token : str
    token_type : str = "bearer"


