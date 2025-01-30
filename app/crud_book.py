from fastapi import HTTPException, Depends

from database import Session, get_db

"""
CRUD операции для книг, просмотр списка всех книг,
взять книгу и  выдать книгу (обе функции включают в себя 
добавление записи о выдаче или возврате книги в таблицу BookTransactions)
"""
from models import User, Book, BookTransactions


def get_book_by_id_or_name(db: Session, book_id: int = None, book_name: str=None) -> Book:
    if book_id:
        book = db.query(Book).filter(Book.id == book_id).one_or_none()
    elif book_name:
        book = db.query(Book).filter(Book.name == book_name).one_or_none()
    else:
        raise HTTPException(400, detail="Укажите ID или название книги")
    if not book:
        raise HTTPException(400, detail="Книга не найдена")
    return book


def get_all_books(db: Session, amount: int=100):
    return db.query(Book).limit(amount).all()

def create_book(data: dict, db:Session):
    try:
        book_obj = Book(name = data['name'],
                        description = data['description'],
                        publication_date = data['publication_date'],
                        author_id = data['author_id'],
                        genre = data['genre'],
                        amount = data['amount']
                        )
        db.add(book_obj)
        db.commit()
        return(f"Книга создана успешно. ID {book_obj.id}")
    except Exception as e:
        db.rollback()
        return (f"Ошибка добавления книги: {e}")


def update_book(db: Session, data: dict):
    try:
        if 'id' in data:
            book = db.query(Book).filter(Book.id == data['id']).one_or_none()
        elif 'name' in data:
            book = db.query(Book).filter(Book.name == data['name']).one_or_none()
        else:
            raise HTTPException(400, detail=f"Чтобы обновить информацию о книге, Укажите ID книги или название")

        #если переданы и айди и название, можно обновить название
        if 'id' in data and 'name' in data:
            setattr(book, 'name', data['name'])
        if 'description' in data:
            setattr(book, 'description', data['description'])
        if 'publication_date' in data:
            setattr(book, 'publication_date', data['publication_date'])
        if 'author_id' in data:
            setattr(book, 'author_id', data['author_id'])
        if 'genre' in data:
            setattr(book, 'genre', data['genre'])
        if 'amount' in data:
            setattr(book, 'amount', data['amount'])
        db.add(book)
        db.commit()
        return book
    except Exception as e:
        db.rollback()
        raise HTTPException(400, detail=f"Не получилось обновить данные о книге: {e}")


def delete_book(book_id: int = None, book_name: str = None, db:Session=Depends(get_db)):
    try:
        if book_id:
            book = db.query(Book).filter(Book.id == book_id).one_or_none()
            answer = book_id
        elif book_name:
            book = db.query(Book).filter(Book.name == book_name).one_or_none()
            answer = book_name
        else:
            raise HTTPException(400, detail=f"Чтобы удалить книгу, укажите имя или ID книги в query params")
        if book is None:
            raise HTTPException(status_code=404, detail="Книга не найдена")

        db.delete(book)
        db.commit()

        return f"Книга {answer} успешно удалена"
    except Exception as e:
        db.rollback()
        raise HTTPException(400, detail=f"Не удалось удалить книгу: {e}")


#создать транзакцию BookTransactions
def create_book_transaction(book_id: int, book:Book, user_id: int, user: User, db: Session, transaction_type: str = 'returned'):
    trans_obj = BookTransactions(book_id=book_id,
                                book=book,
                                user_id=user_id,
                                user=user,
                                transaction_type=transaction_type)
    db.add(trans_obj)
    db.commit()
    print (f"Transaction created: Book '{book.name}' was {transaction_type} by user '{user.name}'")



def book_issue(book_id: int, user: User, db:Session = Depends(get_db)):
    try:
        user_id = user['id']
        user = db.query(User).filter(User.id == user_id).one_or_none()
        book = db.query(Book).filter(Book.id == book_id).one_or_none()
        if user:
            if book:
                user.append_book_to_list(book_id) #добавляем книгу в список книг пользователя
                book.update_book_amount(decrease=True) #уменьшаем количество доступных книг на единицу
            else:
                return f"Книга с ID {book_id} не найдена "
        else:
            return f"Пользователь с ID {user_id} не найден "
        create_book_transaction(book_id=book_id, book=book,
                                user_id=user.id, user=user,
                                transaction_type = 'issued',
                                db=db)
        db.commit()
        return (f"Книга {book_id} выдана читателю {user.name}. Список книг читателя: {user.list_of_issued_books}")
    except Exception as e:
        db.rollback()
        return f"Ошибка выдачи книги читателю: {e}"


def book_return(book_id: int, db: Session, user: User):
    try:
        user_id = user['id']
        user = db.query(User).filter(User.id == user_id).first()
        book = db.query(Book).filter(Book.id == book_id).first()

        if user:
            if book:
                user.delete_book_from_list(book_id)
                book.update_book_amount()
            else:
                return f"Книга с ID {book_id} не найдена "
        else:
            return f"Пользователь с ID {user_id} не найден "

        create_book_transaction(book_id=book_id, book=book,
                                user_id=user_id, user=user,
                                transaction_type='returned',
                                db=db)
        db.commit()
        return (f"Книга {book_id} возвращена читателем {user.name}. Список книг читателя: {user.list_of_issued_books}")
    except Exception as e:
        db.rollback()
        return f"Ошибка возвращения книги: {e}"


