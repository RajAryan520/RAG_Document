
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import select
from table import User

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_URL)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

# query = select(User).where(User.user_id == 1)
# session = Session(engine)
# res = session.execute(query).scalars().all()

# for user in res:
#     print(user)
