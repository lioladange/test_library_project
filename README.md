## Описание проекта:

RESTful API для управления библиотечным каталогом.
Система должна позволяет управлять информацией о книгах, авторах, читателях
и выдачей книг.
В приложении реализована авторизация и аутентификация пользователей с
использованием JWT токенов. Существуют роли: администратор и читатель.
Администратору досутпно больше ресусров, чем читателю.

В проекте есть возможность управления пользователями (crud операции, просмотр
администратором), книгами (crud операции, выдача и возврат книг, просмотр всех книг
пользователями), авторами (crud операции, просмотр всех авторов пользователями).
Выдача книг ограничена: не более 5 книг одному читателю. При выдаче книг автоматически
обновляется список книг у читателя, количество доступных экземпляров книг, добавляется
запись об операции с книгой в таблице транзакции, фиксируется дата выдачи и
дата предполагаемого возврата. Проверки "возвращено ли вовремя" не реализовано.

Приложение позволяет создать таблицы users, books, authors и booktransactions 
в бд, а также заполнить таблицы books и authors фейковой информацией. 
Таблицы миеют следующие поля:
1. books:
     - ID
     - name
     - description
     - publication_date
     - author_id
     - author
     - genre
     - amount
2. authors
     - ID
     - name
     - biography
     - birthdate
3. users
    - id
    - name
    - email
    - password_hash
    - is_admin
    - list_of_issued_books
4. booktransactions
   - id
   - book_id
   - book
   - transaction_type
   - user_id
   - user
   - transaction_date
   - return_date


## Запуск проекта:
1. Создать базу данных posgres в docker командой:

```bash
docker run --name library-13.3 -p 5432:5432 -e POSTGRES_USER=libraryuser -e POSTGRES_PASSWORD=librarypassword -e POSTGRES_DB=librarydb -d postgres:13.3
```

2. Установить необходимые библиотеки из файла requirements.txt с помощью команды:
```bash
pip install -r requirements,txt
```
3.  Чтобы создать 4 таблицы и заполнить таблицы авторы и книги фейковой информацией, 
выполнить команду 'python models.py'.
4. Опционально: чтобы добавить пользователя с правами администратора, выполнить команду (будет создан пользователь "admin" с паролем "admin_pass",
имя и пароль можно изменить в файле, изменив сосотвествующие поля. Можно создавать
неограниченное число администраторов):
```bash
python admin_create.py
```

4. Для локального запуска приложения выполнить команду из папки app: 
```bash
uvicorn main:app --reload --port 8899
```

5. Для остановки приложения, нажмите в консоли ctrl+c.
6. Воспользоваться приложением можно через браузер Postman, а также в 
автогенерируемой документации по адресу  http://127.0.0.1:8899/docs#/ 