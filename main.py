import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Initialize Supabase Client ---
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(url, key)

# --- API Data Models ---
class ChatRequest(BaseModel):
    siteId: str
    question: str

class ChatResponse(BaseModel):
    answer: str

# --- FastAPI App ---
# This line creates the main application object that Uvicorn needs to find.
app = FastAPI()

def get_field_from_question(question: str) -> str:
    """Analyzes the question for keywords to determine which database column to query."""
    question_lower = question.lower()
    
    # Keywords for each topic
    era_keywords = ["when", "era", "built", "year", "age", "constructed"]
    location_keywords = ["where", "location", "located", "address"]
    history_keywords = ["history", "story", "background", "about"]

    if any(keyword in question_lower for keyword in era_keywords):
        return "era"
    if any(keyword in question_lower for keyword in location_keywords):
        return "location"
    if any(keyword in question_lower for keyword in history_keywords):
        return "history"
    
    # Default to description if no specific keywords are found
    return "description"

@app.post("/chat", response_model=ChatResponse)
def chat_handler(request: ChatRequest):
    """Handles chat request by fetching data directly from Supabase based on keywords."""
    
    field_to_fetch = get_field_from_question(request.question)
    
    try:
        response = supabase.table("heritage_sites").select(field_to_fetch).eq("id", request.siteId).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Site ID not found in the database.")
            
        answer = response.data[0].get(field_to_fetch, "Sorry, I could not find that information.")
        
        if not answer:
            answer = "Information for that topic is not available for this site."

        return ChatResponse(answer=answer)

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")
    