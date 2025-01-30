"""
CRUD операции для авторов + просмотр списка всех авторов
"""
import datetime
from fastapi import HTTPException, Depends

from database import Session, get_db
from models import Author



def get_author_by_id(author_id: int, db: Session) -> Author:
    author = db.query(Author).filter(Author.id == author_id).one_or_none()
    if not author:
        raise HTTPException(400, detail="Автор  не найден")
    return author


def get_all_authors(amount: int=100, db:Session = Depends(get_db)):
    return db.query(Author).limit(amount).all()


def create_author(data: dict, db:Session):
    try:
        if ('name' in data) and ('biography' in data) and ('birthdate' in data):        
            author_obj = Author(name=data["name"], biography=data["biography"],
                          birthdate=datetime.datetime.strptime(data["birthdate"], '%d-%m-%Y'))
        else:
            raise HTTPException(400, detail="""Не предоставлены все данные для добавления нового автора. 
            Необходимы поля: name, biography, birthdate""")
        db.add(author_obj)
        db.commit()
        return(f"Автор успешно добавлен в базу данных")
    except Exception as e:
        db.rollback()
        return (f"Registration error: {e}")


#изменить данные об авторе по имени (имя также можно изменить)
def update_author(db: Session, name: str, new_name: str = None, biography: str = None, 
                  birthdate: str = None)->Author:
    author = db.query(Author).filter(Author.name == name).one_or_none()
    if not author:
        raise HTTPException(400, detail="Автор не найден")
    if (not new_name) and (not biography) and (not birthdate):
        raise HTTPException(400, detail=f"Не получилось обновить данные: новые данные не предоставлены")
    try:
        if biography:
            setattr(author, "biography", biography)
        if new_name:
            setattr(author, "name", new_name)
        if birthdate:
            birthdate = datetime.datetime.strptime(birthdate, '%d-%m-%Y')
            setattr(author, "birthdate", birthdate)
        db.commit()
        return author
    except Exception as e:
        db.rollback()
        raise HTTPException(400, detail=f"Не получилось обновить данные автора: {e}")


def delete_author(author_id: int, db:Session=Depends(get_db)):
    author = db.query(Author).filter(Author.id == author_id).one_or_none()
    if author is None:
        raise HTTPException(status_code=404, detail="Автор не найден")

    db.delete(author)
    db.commit()

    return f"Автор с ID {author_id} успешно удален"
