from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import os

def load_rag_vectorstore():
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("api_key"))

    db = Chroma(
        collection_name="wazuh_rag",
        persist_directory="./rag_chroma",
        embedding_function=embeddings
    )

    return db
