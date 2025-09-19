import os
import google.generativeai as genai
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Initialize Clients ---
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(url, key)

# Configure the Google AI client
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_embedding(text: str) -> list[float]:
    """Generates an embedding for a given text using Google's model."""
    try:
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="RETRIEVAL_DOCUMENT"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []

def process_and_store_sites():
    """Fetches data, generates Google embeddings, and stores them."""
    print("Fetching data from heritage_sites table...")
    response = supabase.table("heritage_sites").select("id, name, description, era, location, history").execute()
    
    if not response.data:
        print("No data found.")
        return

    print(f"Found {len(response.data)} sites to process.")
    
    supabase.table("documents").delete().neq("id", -1).execute()
    print("Cleared old documents.")

    for site in response.data:
        content = f"Name: {site['name']}. Location: {site['location']}. Era: {site['era']}. History: {site['history']}. Description: {site['description']}"
        
        print(f"Generating embedding for: {site['name']}...")
        embedding = generate_embedding(content)
        
        if embedding:
            try:
                supabase.table("documents").insert({
                    "content": content,
                    "embedding": embedding
                }).execute()
                print(f"Successfully stored embedding for {site['name']}.")
            except Exception as e:
                print(f"Error storing embedding for {site['name']}: {e}")

if __name__ == "__main__":
    process_and_store_sites()
    print("\nData preparation complete with Google AI embeddings!")