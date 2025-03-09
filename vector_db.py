from pymilvus import MilvusClient, connections, FieldSchema, CollectionSchema, DataType, Collection,MilvusException
from text_extractor import text_embedding,extract_text_from_file
import numpy as np
from sentence_transformers import SentenceTransformer
import uuid
from fastapi import HTTPException


connections.connect(host="127.0.0.1", port="19530")

fields = [
    FieldSchema(name="chunk_id", dtype=DataType.INT64, is_primary=True, auto_id=True),  # Auto-incrementing ID
    FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=36),  # Document ID (UUID)
    FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=36),  # User ID
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=5000),  # Original text chunk
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=384),  # Embedding vector
]
schema = CollectionSchema(fields, description="Document embeddings with chunk IDs")

collection_name = "Document"
collection = Collection(name=collection_name, schema=schema)


def insert_vector(file_path:str,doc_id:uuid.UUID,user_id:int):

    try:
        chunks = extract_text_from_file(file_path)
        vectors = text_embedding(chunks)
        vectors = [vector.tolist() if isinstance(vector, np.ndarray) else vector for vector in vectors]

        # each embedding will have doc_id(uuid) and user_id
        doc_id = str(doc_id)
        user_id = str(user_id)
        #user_id = str(user_id)
        Doc_ids = [doc_id] * len(vectors)
        user_ids = [user_id] * len(vectors)

        data = [Doc_ids, user_ids, chunks,vectors]

        # Insert data into Milvus
        collection.insert(data)
    except MilvusException as e:
        raise HTTPException(status_code=500, detail=f"Milvus insertion failed: {str(e)}")

def delete_vector(doc_id:uuid.UUID):
    try:
        res = collection.delete(f"doc_id in [\"{doc_id}\"]")
        # return {"Deletion Successfull:",res}
    except MilvusException as e:
        raise HTTPException(status_code=500, detail=f"Milvus Deletion failed: {str(e)}")

def query_search(query: str,user_id:int):
    # user input query
    # query will search the embedding from user's doc only
    # return the chunk text
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        query_embedding = model.encode(query)
        nearest_text = []

        results = collection.search(
            data=[query_embedding],
            anns_field="vector",
            param={"metric_type": "cosine", "params": {"nprobe": 10}},
            limit=5,
            expr=f"user_id == \"{user_id}\"",
            output_fields=["text"]
        )

        for result in results:
            for hit in result: 
                nearest_text.append(hit.text) 
        return nearest_text
    
    except MilvusException as e:
        raise HTTPException(status_code=500, detail=f"Milvus Query Search Failed: {str(e)}")

