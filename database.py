import oracledb, os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
print('SQLALCHEMY_DATABAS_URL', DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

print('DATABASE_USER', os.getenv('DATABASE_USER'))
print('DATABASE_PASSWORD', os.getenv('DATABASE_PASSWORD'))
print('DATABASE_DSN', os.getenv('DATABASE_DSN'))

conn = oracledb.connect(user = os.getenv('DATABASE_USER'), 
                        password = os.getenv("DATABASE_PASSWORD"), 
                        dsn = os.getenv("DATABASE_DSN"))
