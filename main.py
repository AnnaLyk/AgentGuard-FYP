# Import FastAPI so it can create an API
from fastapi import FastAPI, Cookie, HTTPException

# Import RedirectResponse so FastAPI can send the user back to Streamlit
from fastapi.responses import RedirectResponse

# Import BaseModel so it can accept a message from the user
from pydantic import BaseModel

# Import requests so Python can send a request to Ollama
import requests

# Import SQLite so FastAPI can check saved sessions
import sqlite3


# ---------------------------------------------------
# 1. CREATE THE FASTAPI APPLICATION
# ---------------------------------------------------

app = FastAPI()


# ---------------------------------------------------
# 2. HOME ENDPOINT
# ---------------------------------------------------

# Create a GET endpoint at the home page "/"
@app.get("/")
def home():

    # Return a simple message to show the API is working
    return {"message": "AgentGuard API is working"}


# ---------------------------------------------------
# 3. SET THE SESSION COOKIE
# ---------------------------------------------------

@app.get("/set-session")
def set_session_cookie(session_id: str):

    # Connect to the AgentGuard database
    connection = sqlite3.connect("agentguard.db")
    cursor = connection.cursor()

    # Check that the session ID exists in the database
    cursor.execute(
        "SELECT user_id FROM sessions WHERE session_id = ?",
        (session_id,)
    )

    session = cursor.fetchone()

    # Close the database connection
    connection.close()

    # If the session does not exist, show an error
    if session is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid session"
        )

    # Send the user back to the Streamlit application
    response = RedirectResponse(
        url="http://localhost:8501",
        status_code=302
    )

    # Store the session ID in a browser cookie
    response.set_cookie(
        key="agentguard_session",
        value=session_id,

        # JavaScript in the browser cannot read this cookie
        httponly=True,

        # Helps protect against some cross-site requests
        samesite="lax",

        # Cookie lasts for one hour
        max_age=3600
    )

    return response


# ---------------------------------------------------
# 4. CHECK THE CURRENT LOGGED-IN USER
# ---------------------------------------------------

@app.get("/whoami")
def who_am_i(
    agentguard_session: str | None = Cookie(default=None)
):

    # If there is no session cookie, the user is not logged in
    if agentguard_session is None:
        raise HTTPException(
            status_code=401,
            detail="Not logged in"
        )

    # Connect to the AgentGuard database
    connection = sqlite3.connect("agentguard.db")
    cursor = connection.cursor()

    # Find the username and role connected to this session
    cursor.execute("""
        SELECT users.username, roles.name
        FROM sessions
        JOIN users ON sessions.user_id = users.id
        JOIN roles ON users.role_id = roles.id
        WHERE sessions.session_id = ?
    """, (agentguard_session,))

    user = cursor.fetchone()

    # Close the database connection
    connection.close()

    # If the session ID is not found in the database
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid session"
        )

    username = user[0]
    role = user[1]

    # Return the trusted user information
    return {
        "username": username,
        "role": role
    }


# ---------------------------------------------------
# 5. DELETE THE SESSION COOKIE
# ---------------------------------------------------

@app.get("/logout-session")
def logout_session(
    agentguard_session: str | None = Cookie(default=None)
):

    # If the browser has an AgentGuard session cookie
    if agentguard_session:

        # Connect to the database
        connection = sqlite3.connect("agentguard.db")
        cursor = connection.cursor()

        # Delete this session from the database
        cursor.execute(
            "DELETE FROM sessions WHERE session_id = ?",
            (agentguard_session,)
        )

        connection.commit()
        connection.close()

    # Send the user back to Streamlit
    response = RedirectResponse(
        url="http://localhost:8501",
        status_code=302
    )

    # Remove the cookie from the browser
    response.delete_cookie("agentguard_session")

    return response


# ---------------------------------------------------
# 6. OLLAMA REQUEST
# ---------------------------------------------------

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

            # Tell Ollama to return the complete answer at once
            "stream": False
        }
    )

    # Convert Ollama's response into Python data
    data = ollama_response.json()

    # Return only the AI's answer
    return {"response": data["response"]}