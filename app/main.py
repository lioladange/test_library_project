from fastapi import FastAPI,Depends
from typing import List

"""
Все основные эндпоинты проекта
"""
from models import User
from database import Session, get_db
from crud_user import get_user_by_id, create_user, update_user, delete_user, get_all_users
from crud_book import get_book_by_id_or_name, update_book, create_book, delete_book, book_return, book_issue, get_all_books
from crud_author import get_author_by_id, create_author, update_author, delete_author, get_all_authors
from auth import login_required, login, admin_required
from validation_models import UserGet, BookGet, AuthorGet


app = FastAPI()


###BOOKS ENDPOINTS

#CREATE BOOK (protected, admin)
#data dict
@app.post('/admin_protected/create_book')
def app_create_book(data: dict, db:Session = Depends(get_db), user: User=Depends(admin_required)):
    return create_book(db=db, data=data)


#READ BOOK (protected, all users)
#query params id or name
@app.get('/protected/get_book', response_model=BookGet )
def app_get_book_by_id_or_name(book_id: int = None, book_name: str = None,
                               db:Session = Depends(get_db),
                               user: User=Depends(login_required))->BookGet:
    return get_book_by_id_or_name(book_id = book_id, book_name = book_name, db=db)


#READ ALL BOOKS, (protected, all users)
@app.get('/protected/get_all_books/{amount}', response_model=List[BookGet])
def app_get_all_books(amount: int=100, db:Session = Depends(get_db),
                      user: User=Depends(login_required))->List[BookGet]:
    return get_all_books(db=db, amount=amount)


#UPDATE BOOK (protected, admin)
#query params data dict
@app.put('/admin_protected/update_book', response_model=BookGet)
def app_update_book(data: dict, db:Session = Depends(get_db), user: User=Depends(admin_required))->BookGet:
    return update_book(db=db, data=data)


#DELETE BOOK (protected, admin)
#query params data dict
@app.delete('/admin_protected/delete_book')
def app_delete_book(book_id: int = None, book_name: str = None, db:Session = Depends(get_db), user: User=Depends(admin_required)):
    return delete_book(book_id=book_id, book_name=book_name, db=db)



@app.get("/")
def root():
    return {"message": "Welcome to the library!"}


#READ USER, protected для админа
#получить всю информацию о  юзере по его айди, включая хэш пароля.
@app.get('/admin_protected/get_user/{user_id}', response_model=UserGet)
def app_get_user_by_id(user_id: int, db:Session = Depends(get_db),
                       admin: User=Depends(admin_required))->UserGet:
    return get_user_by_id(user_id, db=db)

#READ ALL USERS, protected для админа
#получить всю информацию о  юзере по его айди, включая хэш пароля.
@app.get('/admin_protected/get_all_users/{amount}', response_model=List[UserGet])
def app_get_all_users(amount: int=100, db:Session = Depends(get_db),
                       admin: User=Depends(admin_required))->List[UserGet]:
    return get_all_users(db=db, amount=amount)



#READ USER protected, только с авторизацией
#получить всю информацию о текущем юзере (о себе), включая хэш пароля.
#только авторизованный юзер может посмотреть информацию о себе, используя свой токен
@app.get("/protected/get_current_user_info", response_model=UserGet)
def app_protected_get_current_user(user: User = Depends(login_required)) -> UserGet:
    return user


#CREATE
#Регистрация нового пользователя, добавлям его в бд, незащищенное, доступно всем
@app.post('/registration')
def app_registration(data: dict, db:Session = Depends(get_db)):
    return create_user(data, db)


#UPDATE, protected, для админа
#изменить юзера по айди, айди и что изменить передается через query params передается через query params
@app.put('/admin_protected/update_user/{user_id}', response_model=UserGet)
def app_update_user(user_id: int, name: str = None, email: str = None, password: str = None,
                db:Session = Depends(get_db), admin: User=Depends(admin_required)):
    return update_user(db=db, user_id=user_id, new_name=name, email=email, password=password)


#UPDATE, для атворизованного пользователя, обновить информацию о себе
#изменить юзера, что изменить передается через query params
@app.put('/protected/update_user', response_model=UserGet)
def app_protected_update_user(new_name: str = None, email: str = None, password: str = None,
                    user: User = Depends(login_required),
                    db:Session = Depends(get_db)):
    return update_user(name=user['name'], new_name=new_name, email=email, password=password, db=db)



#DELETE, protected, для админа
#удалить юзера по айди
@app.delete('/admin_protected/delete_user/{user_id}')
def app_delete_user(user_id: int, db:Session = Depends(get_db), admin: User=Depends(admin_required)):
    return delete_user(user_id=user_id, db=db)


#LOGIN
#юзер логинится, возвращаем токен
@app.get('/login')
def app_login(name: str,  password: str, db:Session = Depends(get_db)) -> str:
    return login(name, password, db)

#ВЫДАТЬ КНИГУ, protected любой пользователь берет книгу на себя
@app.put("/protected/book_issue/{book_id}")
def app_book_issue(book_id: int, db:Session = Depends(get_db), user: User=Depends(login_required)):
    return book_issue(book_id=book_id, user=user, db=db)


#ВЕРНУТЬ КНИГУ, protected, любой пользователь
@app.put("/protected/book_return/{book_id}")
def app_book_return(book_id: int, db: Session = Depends(get_db), user: User=Depends(login_required)):
    return book_return(book_id=book_id, db=db, user=user)




#AUTHORS

#CREATE AUTHOR, protected, для админа
#Регистрация нового автора, добавлям его в бд
@app.post('/admin_protected/create_author')
def app_create_author(data: dict, db:Session = Depends(get_db), user: User=Depends(admin_required)):
    return create_author(data, db)


#UPDATE AUTHOR, protected, для админа
#изменить юзера по айди, айди и что изменить передается через query params передается через query params
@app.put('/admin_protected/update_author/{author_name}', response_model=AuthorGet)
def app_update_author(author_name: str, new_name: str = None, biography: str = None, birthdate: str = None,
                db:Session = Depends(get_db), admin: User=Depends(admin_required))->AuthorGet:
    return update_author(db=db, name=author_name, new_name=new_name, biography=biography, birthdate=birthdate)

#READ AUTHOR, protected, любой пользователь
#получить всю информацию о текущем юзере (о себе), включая хэш пароля.
#только авторизованный юзер может посмотреть информацию о себе, используя свой токен
@app.get("/protected/get_author/{author_id}", response_model=AuthorGet)
def app_get_author_by_id(author_id: int, db:Session = Depends(get_db),
                         User = Depends(login_required)) -> AuthorGet:
    return get_author_by_id(author_id, db=db)


#READ ALL AUTHORS, protected, любой пользователь
@app.get('/protected/get_all_authors/{amount}', response_model=List[AuthorGet])
def app_get_all_authors(amount: int=100, db:Session = Depends(get_db),
                      User = Depends(login_required))->List[AuthorGet]:
    return get_all_authors(db=db, amount=amount)


#DELETE AUTHOR, protected, для админа
#удалить юзера по айди
@app.delete('/admin_protected/delete_author/{author_id}')
def app_delete_author(author_id: int, db:Session = Depends(get_db), admin: User=Depends(admin_required)):
    return delete_author(author_id=author_id, db=db)

