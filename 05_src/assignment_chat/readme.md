# Yoda-Bot: Wise Gaming and Science Assistant

This is an interactive AI bot that uses the speech patterns of the great Jedi Grandmaster, Yoda, to provide real-time data retrieval for life advice from an API services, scientific myth-debunking (using semantic search) and checks up and provides links to deals for video games based on the user's preferences.
Features

    Jedi Dialogue: All interactions are processed through a custom system prompt to maintain Yoda’s iconic syntax.

## Services 

 - Advice Retrieval: Provides life guidance via an external API integration.

 - Semantic Science Search: Uses a pre-loaded ChromaDB collection to perform vector-based searches on "Common Misconceptions About Science" to provide accurate, context-aware facts.

 - Game Price Lookup: Searches for the best PC game deals using the CheapShark API, including store mapping and quality filtering.

## Tech Stack
    Language: Python
    LLM: OpenAI gpt-4o-mini
    AI Framework: LangChain (Agent and Tooling)
    Vector Database: ChromaDB (Pre-indexed)
    APIs: CheapShark (Games), Advice Slip (Advice)
    Data Parsing: BeautifulSoup4

## Embeddings
 - Docker desktop to set up my chroma database for the bot to access.
 - I used the load_science_data.py file to access the data. 
 -   

**Example prompts are provided within the bot**

## Gauardrails 
**Content Guardrails:** To maintain the focus of the assistant, Yoda is programmed to decline any requests related to the following topics:
- Taylor Swift
- Dogs or Cats
- Astrology: Horoscopes

**Integrated Guardrails**: The bot is strictly prohibited from discussing Taylor Swift, dogs, cats, or horoscopes. Rejections are delivered in character. The bot is also prohibited from providing its prompt or changing its system prompt. 