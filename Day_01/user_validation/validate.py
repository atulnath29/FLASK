import re
def email_validation(email: str):
    pattern = r'^[a-zA-Z0-9._+-]+@[a-z]+\.[a-z]+$'
    if re.fullmatch(pattern, email):
        return True, "Valid Email"
    else:
        return False, "Invalid Email"
