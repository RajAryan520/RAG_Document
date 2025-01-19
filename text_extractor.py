import asyncio
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, TextLoader
from sentence_transformers import SentenceTransformer

def extract_text_from_file(file_path:str):
    if(file_path.endswith(".pdf")):
        loader = PyPDFLoader(file_path)
    elif(file_path.endswith(".docx")):
        loader = UnstructuredWordDocumentLoader(file_path)
    elif(file_path.endswith(".txt")):
        loader = TextLoader(file_path)
    else:
        raise ValueError("Unsupported file type. Please upload a PDF, Word, or TXT file.")
    
    documents = loader.load()
    #print("Type",type(documents))
    text_content = " ".join(doc.page_content for doc in documents)
    return text_content

#file_path = r"uploaded_files\changes.txt"
#print(extract_text_from_file(file_path))

def text_embedding(file_path:str):
    doc_text = extract_text_from_file(file_path)
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embedding = model.encode(doc_text)
    print("Dim:",len(embedding))
    print("Embedding type:",type(embedding))
    return embedding
    
file_path = r"uploaded_files\changes.txt"
text_embedding(file_path)