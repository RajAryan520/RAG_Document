## Document Management & Retrieval System

**Overview**

This project is a secure document management and retrieval system that allows users to upload documents, generate embeddings for efficient search, and retrieve relevant document chunks using semantic search. It is built using FastAPI, PostgreSQL, SQLAlchemy, Milvus.

Features




## Features

- **CRUD Operations**: Users can upload, list, search, and delete documents securely.

- **User Authentication**: Secure user registration and login with JWT authentication.

- **Document Upload**: Users can upload documents, which are stored securely with metadata.

- **Document Chunking**: Large documents are automatically split into smaller text chunks.

- **Vector Embeddings**: Chunks are converted into vector embeddings using Sentence Transformers.

- **Vector Search**: Users can search for relevant document chunks using semantic search powered by Milvus.




## Tech Stack

**Backend:** FastAPI, Python

**Database:** PostgreSQL (SQLAlchemy ORM)

**Vector Database:** Milvus

**Authentication:** JWT, bcrypt

**Machine Learning:** Sentence Transformers
## API Reference

#### Register New User

```
  POST /NewUser
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `Username`      | `string` | **Required**: Username |
| `Password`      | `string` | **Required**: Password |

#### User Login

```
  GET /Login
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `Username`      | `string` | **Required**: Username |
| `Password`      | `string` | **Required**: Password |

#### Upload Document

```
  POST /UploadDoc
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `Input_File` | `UploadFile` | **Required**: The file to be uploaded |
| `Authorization` | `string` | **Required**: JWT Bearer Token for authentication|

#### Delete Document

```
  DELETE /DeleteDoc
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `doc_id`      | `UUID` | **Required**: Document ID |
| `Authorization` | `string` | **Required**: JWT Bearer Token for authentication|

#### Search Query

```
  GET /Query
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `query`      | `string` | **Required**: Query text for searching |
| `Authorization` | `string` | **Required**: JWT Bearer Token for authentication|

#### Get All Documents

```
  GET /AllDoc
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `Authorization` | `string` | **Required**: JWT Bearer Token for authentication|










