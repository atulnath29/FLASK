# Create a user validation custom module

from user_validation.validate import email_validation

email = input("Enter Email: ")
status, message = email_validation(email)

if status:
    print(message)
else:
    print(message)
