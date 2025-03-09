from sqlalchemy.orm import Session
from table import User
from login import Login
from sqlalchemy import insert
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from passlib.context import CryptContext
import uuid
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

def insert_document(db: Session,user_id:str,username:str,doc_name: str,doc_uuid:uuid.UUID):
    try:
        CurrDate = datetime.now().strftime('%Y-%m-%d')
        new_user = User(uuid=doc_uuid,user_id=user_id,username=username,doc_name=doc_name,date_modified=CurrDate)
        
        db.add(new_user)
        #db.commit()
    except SQLAlchemyError as e:
        #db.rollback()
        return {f"Error occurred while inserting the doc:{str(e)}"}

def delete_document(db:Session, uuid: str):
    try:
        # Find the document to delete by UUID
        doc_to_delete = db.query(User).filter(User.uuid == uuid).first()
        
        if doc_to_delete:
            db.delete(doc_to_delete)
        else:
            return {"status": "Document not found"}
    except SQLAlchemyError as e:
        #db.rollback() 
        return {"error": f"Error occurred while deleting the document: {str(e)}"}

def all_docs(db: Session, userid):
    docs = db.query(User).filter(User.user_id == userid).all()
    return docs


#  Login and Create User

def create_user(db: Session,username: str, password: str):
    try:
        
        hashed_pass = pwd_context.hash(password)
        new_user = Login(username = username, password = hashed_pass)
        db.add(new_user)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise ValueError("Username already exist")
    except SQLAlchemyError as e:
        return {"error": f"Error occurred while creating new user: {str(e)}"}



def verify_password(plain_passwod,hashed_password):
    return pwd_context.verify(plain_passwod,hashed_password)

def user_login(db:Session, username:str, password:str):
    try:
        user = db.query(Login).filter(Login.username == username).first()
        if user:
            if verify_password(password,user.password):
                return True
            else:
                return False
        else:
            raise ValueError("Username doesn't exist, Please Enter Valid Username")
    except SQLAlchemyError as e:
        raise ValueError(f"Query error: {str(e)}")




