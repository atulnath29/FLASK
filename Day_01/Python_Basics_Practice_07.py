import re

# Validate whether an entered email ID contains @ 
def email_validation(email: str):
    # # General if else check
    # if email.find("@") == -1:
    #     return False, "invalid email"
    # else:
    #     return True, "valid email"
    # Regex expression check
    pattern = r'^[a-zA-Z0-9._+-]+@[a-z]+\.[a-z]+$'
    if re.fullmatch(pattern,email):
        return True, "Valid Email"
    else:
        return False, "Invalid Email" 

emails = ["billu-6969@gmail.com","billu$6969@gmail.com","billabhai@gmail.com","#$%&*@gmail.com","@gmail.com","billu-696.com"]
for email in emails:
    status, message = email_validation(email)
    if status:
        print(f"{email} is {message}")
    else:
        print(f"{email} is {message}")


# Format a welcome message dynamically using the username in email.
for email in emails:
    status, message = email_validation(email)
    if status:
        username = email.rsplit('@')
        print(f"Welcome, {username[0]}")
