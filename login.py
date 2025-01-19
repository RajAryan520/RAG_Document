from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,BigInteger,String

Base = declarative_base()

class Login(Base):

    __tablename__ = "Login_Details"

    user_id = Column(BigInteger,primary_key=True,autoincrement=True)
    username = Column(String(255),unique=True)
    password = Column(String(255))
