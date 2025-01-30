"""
CRUD операции для пользователей + просмотр списка всекх пользователей
"""
from fastapi import HTTPException, Depends
from typing import List

from database import Session, get_db
from models import User
from validation_models import UserGet


#READ
def get_user_by_id(user_id: int, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).one_or_none()
    if not user:
        raise HTTPException(400, detail="Пользователь не найден")
    return user

#READ ALL
def get_all_users(db: Session, amount: int=100) -> List[User]:
    return db.query(User).limit(amount).all()

#CREATE
def create_user(data: dict, db:Session):
    try:
        user_obj = User(name = data["username"], email = data["email"])
        user_obj.set_password(data["password"])
        db.add(user_obj)
        db.commit()
        return(f"Registration completed")
    except Exception as e:
        db.rollback()
        return (f"Registration error: {e}")

#UPDATE
def update_user(db: Session, name: str, new_name: str = None, email: str = None, password: str = None,
                ) -> UserGet:
    user = db.query(User).filter(User.name == name).one_or_none()
    if not user:
        raise HTTPException(400, detail="Пользователь не найден")
    if (not new_name) and (not password) and (not email):
        raise HTTPException(400, detail=f"Не получилось обновить данные: новые данные не предоставлены")
    try:
        if email:
            setattr(user, "email", email)
        if new_name:
            setattr(user, "name", new_name)
        if password:
            user.set_password(password)
        db.commit()
        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(400, detail=f"Не получилось обновить данные пользователя: {e}")

#DELETE
def delete_user(user_id: int, db:Session=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    db.delete(user)
    db.commit()

    return f"Пользователь с ID {user_id} успешно удален"

