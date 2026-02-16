import os
# Scenario 01
# You are building course listing page. Store course names in a list and display them.
courses = []

while(True):
    course = input("Enter course: ")
    courses.append(course)
    if course == "":
        break

for course in courses:
    print(course)

# Scenario 02
# Store fixed admin roles in tuple and check whether a user role has admin access.
admin_roles = ("Owner", "Editor")
users = {"Babbli":"Viewer", "Bhavan":"Owner", "Babita":"Editor"} # {username : role}

for user in users:
    if users.get(user) in admin_roles:
        print(f"USER: {user} | ADMIN_ACCESS: allowed")
    else:
        print(f"USER: {user} | ADMIN_ACCESS: denied")

# Scenario 03
# Create a dictionary to store user profile data (name, email, role) and printit in areadeable format.
users_profiles = {}
while True:
    user = input("Enter username: ")
    if user == "":
        break
    email = input("Enter email: ")
    role = input("Enter role: ")
    
    users_profiles[user] = {"email": email, "role": role}
    
os.system("cls")
for user in users_profiles:
    print(f"NAME: {user}\nROLE: {users_profiles[user].get("role", "NA")}\nEMAIL: {users_profiles[user].get("email", "NA")}\n")

# Scenario 04
# An API returns details as a dictionary. Extract and display only the student name and marks.
def demo_api():
    name = input("Enter name: ")
    marks = float(input("Enter marks: "))
    hobby = input("Enter hobby: ")
    return {"name":name, "marks": marks, "hobby":hobby}

def student(details: dict):
    os.system("cls")
    print(f"NAME: {details.get("name", "NA")}\nMARKS: {details.get("marks", "NA")}")

student(demo_api())
