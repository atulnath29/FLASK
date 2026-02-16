# Scenario 01
# Create a program that accepts username and password from input and prints a login confirmation message.
def login(username, password):
    allowed_users = {"bob":"bo12"}
    
    if(username in allowed_users):
        if(password == allowed_users[username]):
            print("login successfully!\n")
        else:
            print("Invalid password!\n")
    else:
        print("Invalid username!\n")

uname = input("Enter username: ")
pword = input("Enter password: ")
login(uname, pword)

# Scenario 02
# Build a CLI-based feedback collector that takes user feedback and ratiing and print a thank-you message.
def feedback_collector():
    feedback = ""
    rating = 0
    while(feedback == ""):
        response = input("Enter feedback: ")
        rating = int(input("Enter rating: "))

        if response != "":
            feedback = response

        if response and rating:
            print("Thank you!, this really helps.\n")

feedback_collector()
