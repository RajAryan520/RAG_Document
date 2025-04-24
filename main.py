from datetime import datetime
from fastapi import FastAPI, HTTPException, Request , UploadFile , status , Depends
from database import SessionLocal
from crud import insert_document,delete_document,all_docs,create_user,user_login
from pydantic import BaseModel
from login import Login
from typing import Annotated
from jwt_handler import get_current_user,CurrentUser,create_access_token
from table import User
import uuid
import json
from vector_db import insert_vector,delete_vector,query_search
from contextlib import asynccontextmanager
from kafka_producer import init_kafka_producer,close_kafka_producer,get_producer
from redis_client import redis_client
from es_consumer import es
from logger import logger

@asynccontextmanager
async def lifespan(app : FastAPI):
    await init_kafka_producer()
    yield
    await close_kafka_producer()

app = FastAPI(lifespan=lifespan)

class UUIDRequest(BaseModel):
    uuid: str

class User_IDReq(BaseModel):
    user_id: int

class New_User(BaseModel):
    Username: str
    Password: str

class User_Query(BaseModel):
    query_text: str

class Document_Search(BaseModel):
    doc_search : str


@app.post("/UploadDoc",status_code=status.HTTP_201_CREATED)
async def Upload(Input_File: UploadFile,current_user: Annotated[CurrentUser,Depends(get_current_user)]):

    producer = get_producer()
    logger.debug(f"Producer_UPLOAD_ENDPOINT:{producer}")

    try:
        with open(f"uploaded_files/{Input_File.filename}", "wb") as f:
            f.write(await Input_File.read())
        file_path = f"uploaded_files/{Input_File.filename}"
        db = SessionLocal()
        try:
            if(Input_File.filename == None):
                raise HTTPException(status_code=422,detail=f"File name empty: {str(e)}")
            doc_uuid = uuid.uuid4()
            
            insert_document(db,current_user.id,current_user.username,Input_File.filename,doc_uuid)
            insert_vector(file_path,doc_uuid,current_user.id)

            current_date = datetime.now().strftime('%Y-%m-%d')

            events = {
                "event_type"  : "upload",
                "user_id"     : current_user.id,
                "filename"    : f"{Input_File.filename}",
                "doc_id"      : str(doc_uuid),
                "timestamp"   : current_date,
                "path"        : file_path,
            }
            
            try:
                await producer.send_and_wait("file_events",json.dumps(events).encode())

            except Exception as kafka_error:
                db.rollback()
                raise HTTPException(status_code=500,detail=f"Kafka event publish failed, rolling back database transaction :{str(kafka_error)}")
            
            db.commit()

            return {
                "message": "File uploaded and processed successfully.",
                "user_id": current_user.id,
                "doc_uuid": str(doc_uuid),
                "file_name": Input_File.filename,
           }
        
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400,detail=f"Error occured, rolling back transaction :{str(e)}")

        finally:
            db.close()
    except IOError as e:
        raise HTTPException(status_code=500,detail=f"File Error: {str(e)}")
    
        
@app.delete("/DeleteDoc",status_code=status.HTTP_200_OK)
async def Delete_doc(request:UUIDRequest,current_user:Annotated[CurrentUser,Depends(get_current_user)]):

    producer = get_producer()
    logger.debug(f"Producer_DELETE_ENDPOINT:{producer}")

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
        delete_vector(request.uuid)

        events = {
                "event_type"  : "delete",
                "user_id"     : current_user.id,
                "doc_uuid"    : str(request.uuid),
                "filename"    : document.doc_name,
            }
        
        try:
            await producer.send_and_wait("file_events",json.dumps(events).encode())

        except Exception as kafka_error:
            db.rollback()
            raise HTTPException(status_code=500,detail=f"Kafka event publish failed, rolling back database transaction :{str(kafka_error)}")

        db.commit()
        return {
                "message": "File Deleted Successfully",
                "file_name": document.doc_name,
                "doc_uuid": str(request.uuid),
                "user_id": current_user.id
            }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=f"Error occured, rolling back transaction :{str(e)}")

    finally:
        db.close()


@app.get("/Query",status_code=status.HTTP_200_OK)
def user_query(query:User_Query,current_user:Annotated[CurrentUser,Depends(get_current_user)]):

    try:
        query_text_list = query_search(query.query_text,current_user.id)
        if len(query_text_list) == 0:
            return {"Text":"Null"}
        return [
            {
                f"Text {i}": chunk_text
            }
            for i,chunk_text in enumerate(query_text_list)
        ]
    except Exception as e:
        raise HTTPException(status_code=400,details=f"Error occured:{str(e)}")


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


@app.post("/DocumentSearch",status_code=status.HTTP_200_OK)
async def search_documents(doc_name:Document_Search,current_user:Annotated[CurrentUser,Depends(get_current_user)]):
    
    query_text = doc_name.doc_search.lower()

    cached_key = f"search_cache:{current_user.id}:{query_text}"

    cached_result = await redis_client.get(cached_key)

    if cached_result:
        return json.loads(cached_result)
    
    else:
        # search from ES
        # if result valid then return the result and append to redis cache
        response = await es.search(
            index='documents',
            query = {
                "bool":{
                    "must":[
                        {
                            "match_phrase_prefix":{
                                "filename":query_text
                            }
                        },
                        {
                            "match":{
                                "user_id":current_user.id
                            }
                        }
                    ]
                }
            },
            size=10
        )
        
        results = [hit["_source"]["filename"] for hit in response["hits"]["hits"]]

        if results:
            await redis_client.set(cached_key, json.dumps(results), ex=300)

        return {"matches":results}
          
    

    





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

# extract the chucnks of file and save the embedding with metadata as doc_id,text,user_id --done
# implement rollback of both db postgres nd milvus if anyone fails --done


# query search should work on the users doc only -- done


# add message queue so adding document and its vector does not block the process.






        