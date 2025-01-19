from pymilvus import MilvusClient, connections, FieldSchema, CollectionSchema, DataType, Collection,MilvusException
from text_extractor import text_embedding
import numpy as np
from sentence_transformers import SentenceTransformer
import uuid


connections.connect(host="127.0.0.1", port="19530")

fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=384),
]
schema = CollectionSchema(fields, description="Document embeddings collection")

collection_name = "document"
collection = Collection(name=collection_name, schema=schema)

def insert_vector(file_path:str,doc_id:uuid.UUID):
    vector = text_embedding(file_path)
    vector = vector.tolist() if isinstance(vector, np.ndarray) else vector
  
    data = [[doc_id], [vector]]

    # Insert data into Milvus
    collection.insert(data)

    print(f"Inserted document with ID {doc_id} into collection '{collection_name}'.")


def delete_vector(doc_id:uuid.UUID):
    try:
        res = collection.delete(f"doc_id in {doc_id}")
        return {"Deletion Successfull:",res}
    except MilvusException as e:
        return {"error": f"Error occurred while deleting the document Embedding: {str(e)}"}


def query_search(query: str):
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode(query)

    nearest_text = []

    results = collection.search(
        data=[query_embedding],
        anns_field="vector",
        param={"metric_type": "L2", "params": {"nprobe": 10}},
        limit=5,
        expr=None,
    )
    for result in results:
        for hit in result: 
            nearest_text.append(hit.id) 

    return nearest_text


query_search("what is devops roadmap?")

    