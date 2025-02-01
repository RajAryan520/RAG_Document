import asyncio
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, TextLoader
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

def extract_text_from_file(file_path:str,chunk_size:int = 500,chunk_overlap:int = 50,):

    if(file_path.endswith(".pdf")):
        loader = PyPDFLoader(file_path)
    elif(file_path.endswith(".docx")):
        loader = UnstructuredWordDocumentLoader(file_path)
    elif(file_path.endswith(".txt")):
        loader = TextLoader(file_path)
    else:
        raise ValueError("Unsupported file type. Please upload a PDF, Word, or TXT file.")
    
    documents = loader.load()
    text_content = " ".join(doc.page_content for doc in documents)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap
    )
     
    chunks_text =  text_splitter.split_text(text_content)

    print("Type chunks:",type(chunks_text))
    

    return chunks_text


def text_embedding(doc_text:list):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embedding = []
    for text in doc_text:
        embedding.append(model.encode(text))
    return embedding
    
# file_path = r"C:\Users\RajAr\Desktop\rag_paper.pdf"
#extract_text_from_file(file_path)
#text_embedding(file_path)