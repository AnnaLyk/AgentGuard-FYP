# Import SQLite so Python can read the database
import sqlite3


# ---------------------------------------------------
# 1. CONNECT TO THE DATABASE
# ---------------------------------------------------

# Connect to the existing AgentGuard database
connection = sqlite3.connect("agentguard.db")

# Create a cursor so we can send SQL commands to the database
cursor = connection.cursor()


# ---------------------------------------------------
# 2. CHECK THE ROLES
# ---------------------------------------------------

# Ask the database for every row in the roles table
cursor.execute("SELECT * FROM roles")

# Store all the returned rows
roles = cursor.fetchall()

# Print the roles
print("Roles:")
print(roles)


# ---------------------------------------------------
# 3. CHECK THE PERMISSIONS
# ---------------------------------------------------

# Ask the database for every row in the permissions table
cursor.execute("SELECT * FROM permissions")

# Store all the returned rows
permissions = cursor.fetchall()

# Print the permissions
print("\nPermissions:")
print(permissions)


# ---------------------------------------------------
# 4. CHECK WHICH PERMISSIONS BELONG TO EACH ROLE
# ---------------------------------------------------

cursor.execute("""
SELECT roles.name, permissions.name
FROM role_permissions
JOIN roles ON role_permissions.role_id = roles.id
JOIN permissions ON role_permissions.permission_id = permissions.id
ORDER BY roles.id, permissions.id
""")

# Store the results
role_permissions = cursor.fetchall()

# Print each role with its permission
print("\nRole permissions:")

for role, permission in role_permissions:
    print(f"{role}: {permission}")


# ---------------------------------------------------
# 5. CHECK THE CATEGORIES AND LABELS
# ---------------------------------------------------

cursor.execute("""
SELECT categories.name, labels.name
FROM labels
JOIN categories ON labels.category_id = categories.id
ORDER BY categories.id, labels.id
""")

# Store the results
category_labels = cursor.fetchall()

# Print each category with its label
print("\nCategories and labels:")

for category, label in category_labels:
    print(f"{category}: {label}")


# ---------------------------------------------------
# 6. CLOSE THE DATABASE
# ---------------------------------------------------

# Close the connection when we are finished
connection.close()