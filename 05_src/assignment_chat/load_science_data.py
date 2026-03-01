from bs4 import BeautifulSoup
import chromadb
import os

def load_science_facts():
    """Load science misconceptions into ChromaDB"""
    
    print("Loading science misconceptions into ChromaDB...")
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(__file__)
    print(f"Script directory: {script_dir}")
    
    # Build the path to the HTML file
    html_path = os.path.join(script_dir, "List of common misconceptions about science.htm")
    print(f"Looking for HTML at: {html_path}")
    
    # Check if file exists
    file_exists = os.path.exists(html_path)
    print(f"File exists: {file_exists}")
    
    if not file_exists:
        # List files to debug
        files_in_dir = os.listdir(script_dir)
        print(f"Files in directory: {files_in_dir}")
        print(f"ERROR: HTML file not found!")
        return False
    
    # Parse HTML
    print("Parsing HTML...")
    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    
    texts = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text()) > 5]
    print(f"Extracted {len(texts)} text chunks")
    
    # Load to ChromaDB
    print("Loading into ChromaDB...")
    chroma = chromadb.HttpClient(host="http://localhost:8000")
    
    try:
        chroma.delete_collection("science_facts")
    except:
        pass
    
    collection = chroma.get_or_create_collection("science_facts")
    
    for i, text in enumerate(texts):
        collection.add(documents=[text], ids=[f"science_{i}"])
    
    print(f"Success! Loaded {collection.count()} science facts and misconceptions")
    return True