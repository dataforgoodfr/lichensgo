from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

user_name = os.getenv("user_name")
pwd = os.getenv("pwd")
host = os.getenv("host")
db_name = os.getenv("db_name")

DATABASE_URL = f"postgresql+psycopg2://{user_name}:{pwd}@{host}/{db_name}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def get_session():
    return Session()
