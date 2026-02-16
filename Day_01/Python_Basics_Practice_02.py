# Scenario 01
# Create a user authentication using function

def validator(username, password):
    if(username == "admin" and password == "1234"):
        print("Welcome Admin!")
    else:
        print("Invalid Crededntials")

uname = input("Enter username: ")
pword = input("Enter password: ")
validator(uname, pword)
