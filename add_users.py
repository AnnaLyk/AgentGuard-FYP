# Import the tools needed
import sqlite3
import hashlib
import os
import getpass

# ---------------------------------------------------
# 1. HASH A PASSWORD
# ---------------------------------------------------

# This changes a normal password into a secure hash
# Store the hash in the database, not the real password
def hash_password(password):

    # Create a random value to make the password hash stronger
    salt = os.urandom(16)

    # Create the password hash
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        200000
    )

    # Store the salt and hash together as text
    return salt.hex() + ":" + password_hash.hex()


# ---------------------------------------------------
# 2. CONNECT TO THE DATABASE
# ---------------------------------------------------

connection = sqlite3.connect("agentguard.db")
cursor = connection.cursor()


# ---------------------------------------------------
# 3. TEST THE USERS
# ---------------------------------------------------

users = [
    ("employee1", "Employee"),
    ("hr1", "HR"),
    ("admin1", "Administrator")
]


# ---------------------------------------------------
# 4. ADD EACH USER
# ---------------------------------------------------

for username, role_name in users:

    # Check whether this user already exists
    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        print(f"{username} already exists.")
        continue


    # Find the ID number for this user's role
    cursor.execute(
        "SELECT id FROM roles WHERE name = ?",
        (role_name,)
    )

    role = cursor.fetchone()

    if role is None:
        print(f"Role {role_name} was not found.")
        continue

    role_id = role[0]


    # Ask you to create a password
    # The password will not appear on the screen while you type
    password = getpass.getpass(
        f"Create password for {username}: "
    )

    # Hash the password
    password_hash = hash_password(password)


    # Add the user to the database
    cursor.execute(
        """
        INSERT INTO users (username, password_hash, role_id)
        VALUES (?, ?, ?)
        """,
        (username, password_hash, role_id)
    )

    print(f"{username} added as {role_name}.")


# ---------------------------------------------------
# 5. SAVE AND CLOSE
# ---------------------------------------------------

connection.commit()
connection.close()

print("Test users created.")