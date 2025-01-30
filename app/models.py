"""
Все sqlalchemy модели таблиц и наполнение таблиц Авторы и Книги фейковой информацией.
При запуске этого файла происходит создание бд сброс и создание бд с нуля и заполнение
таблиц Книги и Авторы
"""
from fastapi import HTTPException
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ARRAY, ForeignKey
from passlib.context import CryptContext
import datetime
from faker import Faker
import random

from database import Base, SessionLocal, engine


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

###ОПИСАНИЕ ТАБЛИЦ

#Роль администратора задается в колонке is_admin
class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String) #хранить пароли небезопасно, надо хранить хэши
    is_admin = Column(Boolean, default=False)
    list_of_issued_books = Column(ARRAY(Integer), default=[])

    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)

    def check_password(self, password): #Возвращает True или False
        return pwd_context.verify(password, self.password_hash)

    #изменяет поле пользователя list_of_issued_books: добавляет книгу в список
    def append_book_to_list(self, book_id: int):

        if self.list_of_issued_books is None:
            setattr(self, "list_of_issued_books", [])

        if len(self.list_of_issued_books) >= 5:
            raise HTTPException(status_code=400, detail=f"Превышено максимальное число книг. У пользователя: {len(self.list_of_issued_books)} книг")

        else:
            new_list = self.list_of_issued_books + [book_id]
            setattr(self, "list_of_issued_books", new_list)
            return self

    # изменяет поле пользователя list_of_issued_books: удаляет книгу из списка
    def delete_book_from_list(self, book_id: int):

        if self.list_of_issued_books is None:
            setattr(self, "list_of_issued_books", [])

        if len(self.list_of_issued_books) == 0:
            raise HTTPException(status_code=400, detail="У пользователя нет книг на руках")

        if book_id not in self.list_of_issued_books:
            raise HTTPException(status_code=400, detail="У данного пользователя нет этой книги")
                # добавить как-то проверку, что книга сдается вовремя.
                # можно у юзера сделать колонку со словарем, где ключ это айди книги,
                # а значение это дата разрешеннного возврата, и если текущая дата больше,
                # то выдавать юзеру предупреждение
        else:
            copy_list = self.list_of_issued_books
                    # сложный метод удаления 1 элемента из списка, т.к. простой new_l.remove(book_id)
                    # как-то изменяет типы так, что в базе лист не обновляется потом
                    # возможно, это как-то связано с преобразование типов в sqlalchemy
            flag = 0  # еще не удалили экземпляр
            new_list = []
            for book in copy_list:
                if book not in [book_id]:
                    new_list += [book]
                elif flag == 0:
                    flag += 1
                else:
                    new_list += [book]
            setattr(self, "list_of_issued_books", new_list)
            return self

    def repr(self):
        return {"id" : self.id,
                "name" : self.name,
                "email" : self.email,
                "password_hash" : self.password_hash,
                "is_admin" : self.is_admin,
                "list_of_issued_books" : self.list_of_issued_books}


class Author(Base):
    __tablename__ = "authors"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)  # уникальный ключ
    name = Column(String)
    biography = Column(Text)
    birthdate = Column(DateTime)


class Book(Base):
    __tablename__ = "books"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)  # уникальный ключ
    name = Column(String)
    description = Column(Text)
    publication_date = Column(DateTime)
    author_id = Column(Integer, ForeignKey("authors.id"))
    author = relationship("Author")
    genre = Column(ARRAY(String), default=[])
    amount = Column(Integer)

    #увеличить или уменьшить (если decrease=True) количество доступных книг на 1
    def update_book_amount(self, decrease=False):
        print(f"Было доступных книг: {self.amount}")

        if decrease:
            self.amount -= 1  # уменьшаем количество доступных книг на 1

        else:
            self.amount += 1 # или увеличиваем

        print(f"Стало доступных книг: {self.amount}")

        return self


class BookTransactions(Base):
    __tablename__ = "booktransactions"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key = True)
    book_id = Column(Integer, ForeignKey("books.id"))
    book = relationship("Book")
    transaction_type = Column(String) #issued or returned
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")
    transaction_date = Column(DateTime, default=datetime.datetime.now())
    return_date = Column(DateTime, default=datetime.datetime.now()+datetime.timedelta(days=10))



###ЗАПОЛНЕНИЕ БД ФЕЙКОВОЙ ДАТОЙ
fake = Faker()
genres = ["Fiction", "Romance", "Fantasy", "Science Fiction", "Mystery", "Thriller", "Non-Fiction", "History",
          "Biography", "Poetry"]

def generate_authors(num_authors=100):
    """
    Генерирует авторов, в количестве num_authors
    """
    authors = []
    for _ in range(num_authors):
        name = fake.name()
        biography = fake.text(max_nb_chars=200)
        birthdate = fake.date_of_birth(minimum_age=25, maximum_age=85)
        authors.append({
            "name": name,
            "biography": biography,
            "birthdate": birthdate
        })
    return authors


def generate_books(authors, num_books=100):
    """
    Генерирует книги в количестве num_books
    """
    books = []
    for _ in range(num_books):
        author = random.choice(authors)  # Choose a random author
        name = fake.sentence(nb_words=5)  # Generate a book title
        description = fake.text(max_nb_chars=500)  # Book description
        publication_date = fake.date_this_century()  # Random publication date within this century
        genre = random.sample(genres, 2)  # Randomly select two genres for the book
        amount = random.randint(1, 50)  # Random number of copies available
        books.append({
            "name": name,
            "description": description,
            "publication_date": publication_date,
            "author_id": author["id"],  # Linking the author ID
            "genre": genre,
            "amount": amount
        })
    return books


def insert_authors(authors):
    """
    Добавляет авторов в бд
    """
    session = SessionLocal()
    try:
        # Add each author to the session and commit
        for author in authors:
            author_obj = Author(name=author["name"], biography=author["biography"], birthdate=author["birthdate"])
            session.add(author_obj)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error inserting authors: {e}")
    finally:
        session.close()


def insert_books(books):
    """
    Добавляет книги в бд
    """
    session = SessionLocal()
    try:
        # Add each book to the session and commit
        for book in books:
            book_obj = Book(
                name=book["name"],
                description=book["description"],
                publication_date=book["publication_date"],
                author_id=book["author_id"],
                genre=book["genre"],
                amount=book["amount"]
            )
            session.add(book_obj)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error inserting books: {e}")
    finally:
        session.close()


# Генерация данных и добавление их в бд
def generate_and_insert_data():
    # Generate authors
    authors = generate_authors(num_authors=100)

    # Insert authors into the database
    insert_authors(authors)

    # Assign IDs to authors after inserting them into the database
    session = SessionLocal()
    try:
        authors_from_db = session.query(Author).all()
        for i, author in enumerate(authors_from_db):
            authors[i]["id"] = author.id  # Store the actual ID in the generated data
    except Exception as e:
        print(f"Error fetching authors: {e}")
    finally:
        session.close()

    # Generate books, now that authors have IDs
    books = generate_books(authors, num_books=100)

    # Insert books into the database
    insert_books(books)
    print("Data generation and insertion complete!")

###СОЗДАТЬ БД заново вручную, если не использовать alembic по каким-то причинам
"""
def init_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Tables were created.")
"""

#при запуске файла таблицы Books и Authors наполнятся соответсвующей фейковой информацией (100 записей)
if __name__ == '__main__':
    #init_db()
    generate_and_insert_data()