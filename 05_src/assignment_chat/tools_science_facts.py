# In a new file: tools_science.py

from langchain.tools import tool
import chromadb

@tool
def get_science_fact(query: str) -> str:
    """Search for scientific facts and debunk common misconceptions."""
    
    # chroma = chromadb.HttpClient(host="http://localhost:8000") # old way of connecting to docker
    client = chromadb.PersistentClient(path="./assignment_chat/chroma_db")
    collection = client.get_collection(name="science_facts")
    
    results = collection.query(
        query_texts=[query],
        n_results=3
    )
    
    if not results['documents'][0]:
        return "The Jedi archives, incomplete they must be."
    
    # Format the results
    facts = "\n\n".join(results['documents'][0])
    return f"Science Facts:\n{facts}"