# Import FastAPI so I can create an API
from fastapi import FastAPI

# Import BaseModel so I can accept a message from the user
from pydantic import BaseModel

# Import requests so Python can send a request to Ollama
import requests

# Create the FastAPI application
app = FastAPI()

# Create a GET endpoint at the home page "/"
@app.get("/")
def home():
    # Return a simple message to show the API is working
    return {"message": "AgentGuard API is working"}

# Describe what information the user will send to the API
class PromptRequest(BaseModel):
    prompt: str

# Create an endpoint that sends a prompt to Ollama
@app.post("/ask")
def ask_model(request: PromptRequest):

    # Send the user's prompt to the Ollama API
    ollama_response = requests.post(
      "http://localhost:11434/api/generate",
      json={
          "model": "llama3.2",
          "prompt": request.prompt,
          "stream": False # Tells Ollama to return the finished answer all at once rather than piece by piece.
      }  
    )

    # Convert Ollamas response into Python data
    data = ollama_response.json()

    # Return only the AI's answer
    return {"response": data["response"]}
    