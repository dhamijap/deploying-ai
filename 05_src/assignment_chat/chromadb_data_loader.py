from bs4 import BeautifulSoup

with open("documents/List_of_common_misconceptions_about_science.htm", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# Extract text from paragraphs
misconceptions = []
for p in soup.find_all("p"):
    text = p.get_text().strip()
    if len(text) > 50:  # Skip short paragraphs
        misconceptions.append(text)

print(f"Found {len(misconceptions)} misconceptions")
print(misconceptions[0])  # See what it looks like

import chromadb

chroma = chromadb.HttpClient(host="http://localhost:8000")
collection = chroma.get_or_create_collection(name="science_facts")

# Add each misconception
for i, text in enumerate(misconceptions):
    collection.add(
        documents=[text],
        ids=[f"misconception_{i}"]
    )

print(f"Loaded {collection.count()} items")