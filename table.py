from sqlalchemy import Column, BigInteger, String, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "User_Info"  # Match the table name exactly

    # Match the column names and types from the PostgreSQL table
    uuid = Column(String(255), primary_key=True)  # Corresponds to "UUID" (character)
    user_id = Column(BigInteger, name="user_id")  # Match column name and type
    username = Column(String(255), name="username")  # Match column name, length
    doc_name = Column(String(128), name="doc_name")  # Match column name, length
    date_modified = Column(Date, name="date_modified")  # Match column name

    def __repr__(self):
        return (f"User(uuid={self.uuid},"
                f"user_id={self.user_id},"
                f"user_name={self.username},"
                f"doc_name={self.doc_name},"
                f"modified_date={self.date_modified}") 



