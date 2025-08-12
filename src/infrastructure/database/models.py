from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    ...


class User(Base):
    __tablename__ = "users"
    
    id:             Mapped[int] = mapped_column(Integer, primary_key=True)
    email:          Mapped[str] = mapped_column(String, nullable=False)
    password_hash:  Mapped[str] = mapped_column(String, nullable=False)
    
    
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id:         Mapped[int] = mapped_column(Integer, primary_key=True)
    token:      Mapped[str] = mapped_column(String, nullable=False)
    user_id:    Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
