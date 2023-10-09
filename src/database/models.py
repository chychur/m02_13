from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, Date, String, Boolean, func, Table, UniqueConstraint
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base

from .db import SessionLocal, engine

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), index=True)
    email: Mapped[str] = mapped_column(String(250), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    avatar: Mapped[Optional[str]] = mapped_column(String(255))
    refresh_token: Mapped[Optional[str]] = mapped_column(String(255))
    confirmed: Mapped[bool] = mapped_column(default=False)


class Contact(Base):
    __tablename__ = 'contacts'
    __table_args__ = (
        UniqueConstraint('email', 'user_id', name='unique_contact_user'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), index=True)
    last_name: Mapped[str] = mapped_column(String(100), index=True)
    email: Mapped[str] = mapped_column(String(100), index=True)
    phone_number: Mapped[str] = mapped_column(String(20))
    birth_date: Mapped[str] = mapped_column(Date)
    additional_data: Mapped[Optional[str]] = mapped_column(String(500))
    user_id: Mapped[str] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))

    user: Mapped[User] = relationship(backref="contacts")


if __name__ == '__main__':

    Base.metadata.create_all(bind=engine)


# Dependency
    def get_db():
        db = SessionLocal
        try:
            yield db
        finally:
            db.close()
