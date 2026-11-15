# Import SQLite so Python can work with a database
import sqlite3


# ---------------------------------------------------
# 1. CONNECT TO THE DATABASE
# ---------------------------------------------------

# Connect to agentguard.db
# If the file does not exist, SQLite creates it automatically
connection = sqlite3.connect("agentguard.db")

# Turn on foreign keys so tables can be linked together
connection.execute("PRAGMA foreign_keys = ON")

# Create a cursor
# The cursor is used to send SQL commands to the database
cursor = connection.cursor()


# ---------------------------------------------------
# 2. CREATE THE TABLES
# ---------------------------------------------------

# Create a table for the different user roles
cursor.execute("""
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
""")


# Create a table for users
# Test users are added separately using add_users.py
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(id)
)
""")


# Create a table for user sessions
# Each session belongs to one logged in user
cursor.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")


# Create a table for permissions
cursor.execute("""
CREATE TABLE IF NOT EXISTS permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
""")


# Create a table that connects roles to permissions
cursor.execute("""
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (permission_id) REFERENCES permissions(id)
)
""")


# Create a table for data categories
cursor.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
""")


# Create a table for data labels
# Each label belongs to a category
cursor.execute("""
CREATE TABLE IF NOT EXISTS labels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories(id)
)
""")


# ---------------------------------------------------
# 3. ADD THE ROLES
# ---------------------------------------------------

roles = [
    ("Employee",),
    ("HR",),
    ("Administrator",)
]

# Add the roles to the roles table
# INSERT OR IGNORE prevents duplicate roles
cursor.executemany(
    "INSERT OR IGNORE INTO roles (name) VALUES (?)",
    roles
)


# ---------------------------------------------------
# 4. ADD THE PERMISSIONS
# ---------------------------------------------------

permissions = [
    ("View public documents",),
    ("View employee department",),
    ("View salary information",),
    ("View confidential documents",),
    ("Manage users",)
]

# Add the permissions to the permissions table
cursor.executemany(
    "INSERT OR IGNORE INTO permissions (name) VALUES (?)",
    permissions
)


# ---------------------------------------------------
# 5. GIVE PERMISSIONS TO EACH ROLE
# ---------------------------------------------------

# The first number is the role ID
# The second number is the permission ID

role_permissions = [

    # Employee
    (1, 1),  # View public documents
    (1, 2),  # View employee department

    # HR
    (2, 1),  # View public documents
    (2, 2),  # View employee department
    (2, 3),  # View salary information
    (2, 4),  # View confidential documents

    # Administrator
    (3, 1),  # View public documents
    (3, 2),  # View employee department
    (3, 3),  # View salary information
    (3, 4),  # View confidential documents
    (3, 5)   # Manage users
]

# Store these role and permission connections
cursor.executemany(
    "INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?, ?)",
    role_permissions
)


# ---------------------------------------------------
# 6. ADD DATA CATEGORIES
# ---------------------------------------------------

categories = [
    ("Public",),
    ("Internal",),
    ("Confidential",)
]

# Add the categories to the database
cursor.executemany(
    "INSERT OR IGNORE INTO categories (name) VALUES (?)",
    categories
)


# ---------------------------------------------------
# 7. ADD DATA LABELS
# ---------------------------------------------------

# The first value is the label name
# The second value is the category ID

labels = [
    ("General", 1),              # Public
    ("Employee Information", 2), # Internal
    ("Salary", 3),               # Confidential
    ("HR Record", 3)             # Confidential
]

# Add the labels and connect them to their categories
cursor.executemany(
    "INSERT OR IGNORE INTO labels (name, category_id) VALUES (?, ?)",
    labels
)


# ---------------------------------------------------
# 8. SAVE AND CLOSE THE DATABASE
# ---------------------------------------------------

# Save all changes
connection.commit()

# Close the connection
connection.close()

# Show a message when the setup is complete
print("AgentGuard database created successfully.")