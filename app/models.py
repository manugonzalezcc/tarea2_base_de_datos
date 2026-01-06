"""Database models for the library management system."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from advanced_alchemy.base import BigIntAuditBase
import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


book_categories = sa.Table(
    "book_categories",
    BigIntAuditBase.metadata,
    sa.Column(
        "book_id",
        sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
        sa.ForeignKey("books.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "category_id",
        sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
        sa.ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(BigIntAuditBase):
    """User model with audit fields."""

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(unique=True)
    fullname: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    phone: Mapped[str | None]
    address: Mapped[str | None]
    is_active: Mapped[bool] = mapped_column(default=True)
    password: Mapped[str]

    loans: Mapped[list["Loan"]] = relationship(back_populates="user")

    reviews: Mapped[list["Review"]] = relationship(back_populates="user")


class Book(BigIntAuditBase):
    """Book model with audit fields."""

    __tablename__ = "books"

    title: Mapped[str] = mapped_column(unique=True)
    author: Mapped[str]
    isbn: Mapped[str] = mapped_column(unique=True)
    pages: Mapped[int]
    published_year: Mapped[int]

    publisher: Mapped[str | None]
    language: Mapped[str]
    description: Mapped[str | None] = mapped_column(sa.Text())
    stock: Mapped[int] = mapped_column(default=1)

    loans: Mapped[list["Loan"]] = relationship(back_populates="book")

    categories: Mapped[list["Category"]] = relationship(
        secondary=book_categories,
        back_populates="books",
    )

    reviews: Mapped[list["Review"]] = relationship(back_populates="book")


class Category(BigIntAuditBase):
    """Category model for books."""

    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]

    books: Mapped[list[Book]] = relationship(
        secondary=book_categories,
        back_populates="categories",
    )

class LoanStatus(str, Enum):
    """Loan status values."""

    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"


class Loan(BigIntAuditBase):
    """Loan model with audit fields."""

    __tablename__ = "loans"

    loan_dt: Mapped[date] = mapped_column(default=date.today)
    return_dt: Mapped[date | None]
    due_date: Mapped[date]
    fine_amount: Mapped[Decimal | None] = mapped_column(sa.Numeric(10, 2))
    status: Mapped[LoanStatus] = mapped_column(
        sa.Enum(LoanStatus, name="loanstatus"),
        default=LoanStatus.ACTIVE,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))

    user: Mapped[User] = relationship(back_populates="loans")
    book: Mapped[Book] = relationship(back_populates="loans")


class Review(BigIntAuditBase):
    """Review model for book reviews."""

    __tablename__ = "reviews"

    rating: Mapped[int]
    comment: Mapped[str]
    review_date: Mapped[date] = mapped_column(default=date.today)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))

    user: Mapped[User] = relationship(back_populates="reviews")
    book: Mapped[Book] = relationship(back_populates="reviews")


@dataclass
class PasswordUpdate:
    """Password update request."""

    current_password: str
    new_password: str


@dataclass
class BookStats:
    """Book statistics data."""

    total_books: int
    average_pages: float
    oldest_publication_year: int | None
    newest_publication_year: int | None
