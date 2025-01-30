"""
Создаем пользователя с правами администратора
"""
from models import User
from database import get_db


db = get_db()

admin = User(name = "admin", email = "no_mail", is_admin = True)
admin.set_password("adminpass")
db.add(admin)
db.commit()
print("Администратор создан")