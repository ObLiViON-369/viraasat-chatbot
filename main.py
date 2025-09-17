import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# --- Initialize Supabase ---
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
app = FastAPI()

# --- Chatbot Logic ---
def get_field_from_question(question: str) -> str:
    """Determines which database column to query based on keywords."""
    question_lower = question.lower()
    if "when" in question_lower or "era" in question_lower or "built" in question_lower:
        return "era"
    if "where" in question_lower or "location" in question_lower:
        return "location"
    # Default to the main description for any other question
    return "description"

@app.post("/chat", response_model=ChatResponse)
def chat_handler(request: ChatRequest):
    """Handles chat request, gets keyword, and fetches data from Supabase."""
    
    # 1. Determine which piece of data to get
    field_to_fetch = get_field_from_question(request.question)
    
    try:
        # 2. Query the 'heritage_sites' table in Supabase
        response = supabase.table("heritage_sites").select(field_to_fetch).eq("id", request.siteId).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Site ID not found in the database.")
            
        # 3. Extract the answer from the database response
        answer = response.data[0].get(field_to_fetch, "Sorry, I could not find that information.")
        
        return ChatResponse(answer=answer)

    except Exception as e:
        # This will catch any errors from the database
        raise HTTPException(status_code=500, detail=str(e))