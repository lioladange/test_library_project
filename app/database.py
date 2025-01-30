from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

"""
Создание необходимых переменных для подключения к бд
"""
import os
from dotenv import load_dotenv


load_dotenv()

SQLALCHEMY_DATABASE_URL = os.environ["SQLALCHEMY_DATABASE_URL"]
# Create the database engine to connect to the database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Set up sessionmaker for creating sessions to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the base class for declarative models
Base = declarative_base()

Session = SessionLocal()

def get_db():
    with SessionLocal() as db:
        return db

