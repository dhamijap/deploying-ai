from bs4 import BeautifulSoup
import chromadb
import os
import time

def load_science_facts():
    """Load science misconceptions into a local ChromaDB persistent store"""
    
    print("\n--- Starting Science Data Load ---")
    
    # 1. FIXED PATHING: Always relative to THIS file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "chroma_db")
    html_path = os.path.join(script_dir, "List of common misconceptions about science.htm")
    
    print(f"Target Database: {db_path}")
    
    # 2. Check for HTML source
    if not os.path.exists(html_path):
        print(f"ERROR: HTML file not found at {html_path}")
        return False
    
    # 3. Parse HTML
    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    
    # Extract paragraphs and list items
    texts = [p.get_text().strip() for p in soup.find_all(["p", "li"]) if len(p.get_text().strip()) > 20]
    print(f"Extracted {len(texts)} text chunks.")
    
    if len(texts) == 0:
        print("ERROR: No text extracted. Check your HTML parsing logic.")
        return False

    # 4. Initialize Chroma (Persistent Mode)
    client = chromadb.PersistentClient(path=db_path)
    
    # Wipe old collection to ensure a clean 'bake'
    try:
        client.delete_collection("science_facts")
        print("Old collection cleared.")
    except:
        pass
    
    collection = client.create_collection("science_facts")
    
    # 5. Add Documents
    print("Embedding data... please wait.")
    collection.add(
        documents=texts,
        ids=[f"science_{i}" for i in range(len(texts))]
    )
    
    # 6. VERIFY & FLUSH
    final_count = collection.count()
    print(f"SUCCESS: {final_count} facts baked into {db_path}")
    
    # Small pause to ensure Windows finishes file writing
    time.sleep(1)
    return True

# This allows you to run the script directly from your terminal
if __name__ == "__main__":
    load_science_facts()