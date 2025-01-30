"""
Pydantic модели для валиадции ответов сервера
"""
from pydantic import BaseModel
import datetime


class UserGet(BaseModel):
    name: str
    email: str
    password_hash: str
    is_admin: bool
    list_of_issued_books: list

    class Config:
        from_attributes = True


class BookGet(BaseModel):
    name: str
    description: str
    publication_date: datetime.date
    author_id: int
    genre: list
    amount: int

    class Config:
        from_attributes = True


class AuthorGet(BaseModel):
    name: str
    biography: str
    birthdate: datetime.date

    class Config:
        from_attributes = True


"""
class TransactionGet(BaseModel):
    book_id: int
    book: Book
    transaction_type: str
    user_id: int
    user: User
    transaction_date: datetime
    return_date: datetime
"""