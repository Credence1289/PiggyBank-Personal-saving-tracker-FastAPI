from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Column, Boolean, ForeignKey, DateTime
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    user_id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    name:Mapped[str] = mapped_column(String)
    mobile_no:Mapped[str] = mapped_column(String(20), unique=True)
    email:Mapped[str] = mapped_column(String, unique=True)
    hashed_password:Mapped[str] = mapped_column(String, nullable = False)

    piggybanks = relationship(
        "PiggyBank",
        back_populates="user",
        cascade="all, delete-orphan"
    )

class PiggyBank(Base):
    __tablename__ = "piggybank"

    piggybank_id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id:Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id", ondelete = "CASCADE"))
    hashed_passwordpb:Mapped[str] = mapped_column(String, nullable = False)
    name:Mapped[str] = mapped_column(String)
    target_amount:Mapped[float] = mapped_column(Float)
    balance:Mapped[float] = mapped_column(Float, default = 0.0)
    is_target_active:Mapped[bool] = mapped_column(Boolean, default = True)

    user = relationship("User", back_populates="piggybanks")

    transactions = relationship(
        "Transaction",
        back_populates="piggybank",
        cascade="all, delete-orphan"
    )

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    piggybank_id:Mapped[int] = mapped_column(Integer, ForeignKey("piggybank.piggybank_id", ondelete = "CASCADE"))
    type:Mapped[str] = mapped_column(String)
    amount:Mapped[float] = mapped_column(Float)
    time_stamp:Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable = False)

    piggybank = relationship("PiggyBank", back_populates="transactions")


