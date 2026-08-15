import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from database.models import Base
from sqlalchemy.orm import Session

load_dotenv()


USER = os.getenv("DATABASE_USER")
PASSWORD = os.getenv("DATABASE_PASSWORD")
HOST = os.getenv("DATABASE_HOST")
PORT = os.getenv("DATABASE_PORT")
DBNAME = os.getenv("DATABASE_NAME")


DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
    f"?sslmode=require"
)


engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool
)

def get_db():
    with Session(engine) as session:
        yield session

if __name__ == "__main__":

    try:
        with engine.connect() as connection:
            print("Connection successful!")

        Base.metadata.create_all(engine)

        print("Database tables created!")

    except Exception as e:
        print(f"Failed to connect: {e}")