# Import the tools needed
import streamlit as st
import sqlite3
import hashlib
import hmac
import secrets


# ---------------------------------------------------
# 1. CHECK A PASSWORD
# ---------------------------------------------------

# Check whether the password entered by the user
# matches the password stored in the database
def verify_password(password, stored_password):

    # Split the stored value into the salt and password hash
    salt_hex, hash_hex = stored_password.split(":")

    # Change the salt back into bytes
    salt = bytes.fromhex(salt_hex)

    # Hash the password the user entered
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        200000
    )

    # Compare the entered password hash
    # with the stored password hash
    return hmac.compare_digest(
        password_hash.hex(),
        hash_hex
    )


# ---------------------------------------------------
# 2. CHECK THE USER LOGIN
# ---------------------------------------------------

def check_login(username, password):

    # Connect to the AgentGuard database
    connection = sqlite3.connect("agentguard.db")
    cursor = connection.cursor()

    # Find the user and their role
    cursor.execute("""
        SELECT users.password_hash, roles.name
        FROM users
        JOIN roles ON users.role_id = roles.id
        WHERE users.username = ?
    """, (username,))

    user = cursor.fetchone()

    connection.close()

    # Username was not found
    if user is None:
        return None

    stored_password = user[0]
    role = user[1]

    # Check the password
    if verify_password(password, stored_password):
        return role

    return None


# ---------------------------------------------------
# 3. CREATE A DATABASE SESSION
# ---------------------------------------------------

def create_session(username):

    # Create a random session ID
    session_id = secrets.token_urlsafe(32)

    # Connect to the database
    connection = sqlite3.connect("agentguard.db")
    cursor = connection.cursor()

    # Find the user's ID
    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()

    if user is None:
        connection.close()
        return None

    user_id = user[0]

    # Save the session
    cursor.execute("""
        INSERT INTO sessions (session_id, user_id)
        VALUES (?, ?)
    """, (session_id, user_id))

    connection.commit()
    connection.close()

    return session_id


# ---------------------------------------------------
# 4. GET A USER FROM A SAVED SESSION
# ---------------------------------------------------

def get_user_from_session(session_id):

    # Connect to the database
    connection = sqlite3.connect("agentguard.db")
    cursor = connection.cursor()

    # Find the username and role connected
    # to this session ID
    cursor.execute("""
        SELECT users.username, roles.name
        FROM sessions
        JOIN users ON sessions.user_id = users.id
        JOIN roles ON users.role_id = roles.id
        WHERE sessions.session_id = ?
    """, (session_id,))

    user = cursor.fetchone()

    connection.close()

    return user


# ---------------------------------------------------
# 5. CREATE STREAMLIT SESSION VALUES
# ---------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "username" not in st.session_state:
    st.session_state["username"] = None

if "role" not in st.session_state:
    st.session_state["role"] = None

if "session_id" not in st.session_state:
    st.session_state["session_id"] = None


# ---------------------------------------------------
# 6. CHECK FOR AN EXISTING COOKIE
# ---------------------------------------------------

# Read the AgentGuard cookie from the browser
cookie_session_id = st.context.cookies.get("agentguard_session")


# If a cookie exists but Streamlit does not yet know
# that the user is logged in, restore the session
if cookie_session_id and not st.session_state["logged_in"]:

    user = get_user_from_session(cookie_session_id)

    if user:
        st.session_state["logged_in"] = True
        st.session_state["username"] = user[0]
        st.session_state["role"] = user[1]
        st.session_state["session_id"] = cookie_session_id


# ---------------------------------------------------
# 7. LOGIN PAGE
# ---------------------------------------------------

st.title("NovaCore Staff Portal")
st.write("Secure internal access for NovaCore staff")


# If nobody is logged in
if not st.session_state["logged_in"]:

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        # Check the username and password
        role = check_login(username, password)

        if role:

            # Create the database session
            session_id = create_session(username)

            # Send the current browser tab to FastAPI
            # FastAPI will set the cookie and return
            # the user to Streamlit
            cookie_url = (
                "http://localhost:8000/set-session"
                f"?session_id={session_id}"
            )

            st.html(
                f"""
                <script>
                    window.location.replace("{cookie_url}");
                </script>
                """,
                unsafe_allow_javascript=True
            )

            st.stop()

        else:
            st.error("Invalid username or password")


# ---------------------------------------------------
# 8. LOGGED-IN PAGE
# ---------------------------------------------------

else:

    st.success("Login successful")

    st.write(
        f"Logged in as: {st.session_state['username']}"
    )

    st.write(
        f"Role: {st.session_state['role']}"
    )


    # ---------------------------------------------------
    # LOGOUT
    # ---------------------------------------------------

    if st.button("Logout"):

        # Send the current tab to FastAPI
        # FastAPI deletes the database session
        # and removes the browser cookie
        logout_url = "http://localhost:8000/logout-session"

        st.html(
            f"""
            <script>
                window.location.replace("{logout_url}");
            </script>
            """,
            unsafe_allow_javascript=True
        )

        st.stop()