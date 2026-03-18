from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from .auth.security import hash_password, verify_password
from .db import db_models
from .db.session import get_db
from .auth.token import create_access_token
from .auth.gate import current_user
from .db.models import UserCreate, PiggyBankCreate, Token

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================== USER ENDPOINTS ======================

@app.post("/users")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(db_models.User)
        .filter(
            (db_models.User.email == user.email) |
            (db_models.User.mobile_no == user.mobile_no)
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists with this email or mobile number"
        )

    new_user = db_models.User(
        name=user.name,
        mobile_no=user.mobile_no,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "user_id": new_user.user_id,
        "message": "User created successfully"
    }


@app.post("/user/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(db_models.User)
        .filter(db_models.User.email == form_data.username)
        .first()
    )
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(user_id=user.user_id, role="user")
    return Token(access_token=access_token, token_type="bearer")


@app.delete("/users")
def delete_user(current: dict = Depends(current_user), db: Session = Depends(get_db)):
    db.delete(current["user"])
    db.commit()
    return {"message": "User deleted successfully"}


# ====================== PIGGYBANK ENDPOINTS ======================

@app.post("/users/piggybank")
def create_piggybank(
    data: PiggyBankCreate,
    db: Session = Depends(get_db),
    current: dict = Depends(current_user),
):
    piggybank = db_models.PiggyBank(
        user_id=current["user"].user_id,
        hashed_passwordpb=hash_password(data.passwordpb),
        name=data.name,
        target_amount=data.target_amount,
        balance=0.0,
    )
    db.add(piggybank)
    db.commit()
    db.refresh(piggybank)
    return {
        "piggybank_id": piggybank.piggybank_id,
        "message": "PiggyBank created successfully",
    }


@app.delete("/users/piggybank/{piggybank_id}")
def delete_piggybank_id(
    piggybank_id: int,
    name: str,
    passwordpb: str,
    db: Session = Depends(get_db),
    current: dict = Depends(current_user),
):
    piggybank = (
        db.query(db_models.PiggyBank)
        .filter(
            db_models.PiggyBank.piggybank_id == piggybank_id,
            db_models.PiggyBank.user_id == current["user"].user_id,
            db_models.PiggyBank.name == name,
        )
        .first()
    )
    if not piggybank:
        raise HTTPException(status_code=404, detail="PiggyBank not found")

    if not verify_password(passwordpb, piggybank.hashed_passwordpb):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    db.delete(piggybank)
    db.commit()
    return {"message": "PiggyBank successfully deleted"}


@app.get("/users/piggybank")
def show_all_piggy(db: Session = Depends(get_db), current: dict = Depends(current_user)):
    piggybanks = (
        db.query(db_models.PiggyBank)
        .filter(db_models.PiggyBank.user_id == current["user"].user_id)
        .all()
    )
    if not piggybanks:
        raise HTTPException(status_code=404, detail="No piggybanks found")

    return [
        {
            "piggybank_id": p.piggybank_id,
            "name": p.name,
            "balance": p.balance,
        }
        for p in piggybanks
    ]


@app.get("/users/piggybank/{piggybank_id}")
def show_piggy(
    piggybank_id: int,
    db: Session = Depends(get_db),
    current: dict = Depends(current_user),
):
    piggybank = (
        db.query(db_models.PiggyBank)
        .filter(
            db_models.PiggyBank.piggybank_id == piggybank_id,
            db_models.PiggyBank.user_id == current["user"].user_id,
        )
        .first()
    )
    if not piggybank:
        raise HTTPException(status_code=404, detail="PiggyBank not found")

    return {
        "piggybank_id": piggybank.piggybank_id,
        "user_id": piggybank.user_id,
        "name": piggybank.name,
        "balance": piggybank.balance,
        "target_amount": piggybank.target_amount,
        "is_target_active": piggybank.is_target_active,
    }


# ====================== TRANSACTION ENDPOINTS ======================

@app.post("/users/piggybank/{piggybank_id}/deposit")
def create_piggybank_deposit(
    piggybank_id: int,
    amount: float,
    db: Session = Depends(get_db),
    current: dict = Depends(current_user),
):
    piggybank = (
        db.query(db_models.PiggyBank)
        .filter(
            db_models.PiggyBank.piggybank_id == piggybank_id,
            db_models.PiggyBank.user_id == current["user"].user_id,
        )
        .first()
    )
    if not piggybank:
        raise HTTPException(status_code=404, detail="PiggyBank not found")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")

    piggybank.balance += amount

    new_transaction = db_models.Transaction(
        piggybank_id=piggybank.piggybank_id,
        type="Deposit",
        amount=amount,
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(piggybank)

    return {
        "message": f"{amount} credited successfully into {piggybank.name}. "
                   f"Your current balance is {piggybank.balance}"
    }


@app.post("/users/piggybank/{piggybank_id}/withdraw")
def create_piggybank_withdraw(
    piggybank_id: int,
    amount: float,
    db: Session = Depends(get_db),
    current: dict = Depends(current_user),
):
    piggybank = (
        db.query(db_models.PiggyBank)
        .filter(
            db_models.PiggyBank.piggybank_id == piggybank_id,
            db_models.PiggyBank.user_id == current["user"].user_id,
        )
        .first()
    )
    if not piggybank:
        raise HTTPException(status_code=404, detail="PiggyBank not found")

    if piggybank.balance < piggybank.target_amount:
        raise HTTPException(status_code=403, detail="Target not completed yet")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")
    if piggybank.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    piggybank.balance -= amount

    new_transaction = db_models.Transaction(
        piggybank_id=piggybank.piggybank_id,
        type="Withdraw",
        amount=amount,
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(piggybank)

    return {"message": f"{amount} successfully withdrawn from {piggybank.name}."}


@app.get("/users/piggybank/{piggybank_id}/transaction")
def show_transaction(
    piggybank_id: int,
    db: Session = Depends(get_db),
    current: dict = Depends(current_user),
):
    # Ownership check first
    piggybank = (
        db.query(db_models.PiggyBank)
        .filter(
            db_models.PiggyBank.piggybank_id == piggybank_id,
            db_models.PiggyBank.user_id == current["user"].user_id,
        )
        .first()
    )
    if not piggybank:
        raise HTTPException(status_code=404, detail="PiggyBank not found")

    transactions = (
        db.query(db_models.Transaction)
        .filter(db_models.Transaction.piggybank_id == piggybank_id)
        .all()
    )
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found")

    return transactions