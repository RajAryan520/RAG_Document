from datetime import datetime
from fastapi import FastAPI, HTTPException, Request , UploadFile , status , Depends
from database import SessionLocal
from crud import insert_document,delete_document,all_docs,create_user,user_login,create_access_token
from pydantic import BaseModel
from login import Login
from typing import Annotated
from jwt_handler import get_current_user,CurrentUser
from table import User
import uuid
from vector_db import insert_vector

app = FastAPI()

class UUIDRequest(BaseModel):
    uuid: str

class User_IDReq(BaseModel):
    user_id: int

class New_User(BaseModel):
    Username: str
    Password: str


@app.post("/UploadDoc",status_code=status.HTTP_201_CREATED)
async def Upload(Input_File: UploadFile,current_user: Annotated[CurrentUser,Depends(get_current_user)]):

    try:
        with open(f"uploaded_files/{Input_File.filename}", "wb") as f:
            f.write(await Input_File.read())
        file_path = f"uploaded_files/{Input_File.filename}"
        db = SessionLocal()
        try:
            if(Input_File.filename == None):
                raise HTTPException(status_code=422,details=f"File name empty: {str(e)}")
            doc_uuid = uuid.uuid4()
            insert_document(db,current_user.id,current_user.username,Input_File.filename,doc_uuid)
            insert_vector(file_path,doc_uuid)
        finally:
            db.close()
    except IOError as e:
        raise HTTPException(status_code=500,details=f"File Error: {str(e)}")
    return {"status: " "File Uploaded Successfully"}
        
@app.delete("/DeleteDoc",status_code=status.HTTP_200_OK)
async def Delete_doc(request:UUIDRequest,current_user:Annotated[CurrentUser,Depends(get_current_user)]):

    db = SessionLocal()

    try:
        document = db.query(User).filter(User.uuid == request.uuid).first()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not Found")
        
        if document.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to delete this document"
            )
        delete_document(db,request.uuid)

    
    finally:
        db.close()

    return {"status: " "File Deleted Successfully"}

@app.get("/AllDoc", status_code=status.HTTP_200_OK)
def user_docs(current_user:Annotated[CurrentUser,Depends(get_current_user)]):
    db = SessionLocal()
    try:
        docs_list = all_docs(db,current_user.id)
    finally:
        db.close()

    if not docs_list:
        raise HTTPException(status_code=404, detail="No document found for the given user_id")
    
    return [
        {
            "UUID": doc.uuid.strip(),
            "User-ID": doc.user_id,
            "Doc-Name": doc.doc_name.strip(),
            "Modified-Date": str(doc.date_modified),
        }
        for doc in docs_list
    ]
    
@app.post("/NewUser", status_code=status.HTTP_201_CREATED)
def register(request: New_User):

    db = SessionLocal()
    try:
        # check if username is already there in db, if there then raise exeception
        existing_user = db.query(Login).filter(Login.username == request.Username).first()
        if existing_user:
            raise HTTPException(
                status_code=400,detail="Username already exist. Please choose another username"
            )
        # Hash the password before adding to db
        create_user(db,request.Username,request.Password)
    finally:
        db.close()
    return {"User Created Successfully"}


@app.get("/Login",status_code=status.HTTP_202_ACCEPTED)
def login(request: New_User):
    db = SessionLocal()
    try:
        user = user_login(db,request.Username,request.Password)
        if user:
            
            # return JWT token so OAuth
            access_token = create_access_token(data={"sub":request.Username},)
            return {"message": "Successfully Logged In","access_token":access_token,"token_type":"bearer"}
        
        else:
            return {"message": "Invalid username or password"}
    finally:
        db.close()

# Login and generate a token -done
# get_current_user -done
# all endpoint needs a token will display info related to current_user -done

# option to see all the upload file  -done
# Option to perform crud operation (only deletion of doc) -done

# Option to upload txt file.  -done

# the file uploaded by user will pass through the kafka queue
# Extract the text from file through langchain -- done
# Give the text to the model and generate the embedding --done
# store the embedding in vector db --done
# take user query , generate its embedding and store in the vector db ( or without storing we will fetch k-nearest vector) --done
# take the fetched k-nearest vector, and query embedding to LLMs to address the query based on most accurate document 

# implement rollback of both db postgres nd milvus if anyone fails