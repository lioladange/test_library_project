"""
Функции для авторизации пользователей и админа
"""
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials
from fastapi import HTTPException, Depends, Security
import os
from dotenv import load_dotenv

from database import Session
from models import User


#загружаем переменные окружения
load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"]

#объект fastapi_jwt, позволяющий работать с токенами: выпускать, расшифровывать и тд
access_security = JwtAccessBearer(secret_key=SECRET_KEY, algorithm=ALGORITHM)



#получить юзера из переданного токена, то есть расшифровать токен с целью понять, какой юзер в данный момент,
#то есть грубо говоря проверка авторизации. subject - это данные юзера
def get_current_user(credentials: JwtAuthorizationCredentials = Security(access_security)):
    return credentials.subject


#выносим как отдельную функцию, чтобы переиспользовать как depends во всех эндпоинтах, где
#требуется аутентификация (т.е. доступ для авторизованных пользователей)
def login_required(user: User = Depends(get_current_user)) -> User:
    if user is None:
        raise HTTPException(401,
                            detail="Пользовать не авторизован",
                            headers={"WWW-Authenticate": "Bearer"})
                            #The HTTP WWW-Authenticate response header advertises the HTTP authentication
                            #methods (or challenges) that might be used to gain access to a specific resource.
    return user


#доступ администратора
def admin_required(user: User = Depends(get_current_user)) -> User:
    if user is None:
        raise HTTPException(401,
                            detail="Пользовать не авторизован",
                            headers={"WWW-Authenticate": "Bearer"})
                            #The HTTP WWW-Authenticate response header advertises the HTTP authentication
                            #methods (or challenges) that might be used to gain access to a specific resource.
    if user["is_admin"]:
        return user
    else:
        raise HTTPException(400,
                            detail="Нужны права администратора",
                            headers={"WWW-Authenticate": "Bearer"})
        # The HTTP WWW-Authenticate response header advertises the HTTP authentication
        # methods (or challenges) that might be used to gain access to a specific resource.


#логинимся и получаем токен доступа
def login(name: str,  password: str, db:Session) -> str:
    user = db.query(User).filter(User.name == name).one_or_none()
    if user:
        if user.check_password(password):
            token = access_security.create_access_token(subject=user.repr())
            return token
        else:
            raise HTTPException(status_code=400, detail='Неверный пароль')
    raise HTTPException(status_code=400, detail='Invalid login')


