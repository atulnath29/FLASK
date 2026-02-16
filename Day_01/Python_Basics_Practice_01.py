# Scenario 01
# You are developing a user registration module for a web application.
# Store user details such as username, age, email and is active using appropriate data types and display them.
username = input("Enter username: ")
age = input("Enter age: ")
email = input("Enter email: ")
isActive = True

print(f"USER: {username} is {age} year old, EMAIL: {email} is active {isActive}\n")

# Scenario 02
# A startup is building a priceing calculator API.
# Store product price, discount percentage, and final price using correct data types and print rhe result.
prodPrice = float(input("Enter price: "))
discountRate = float(input("Enter discount: "))
finalPrice = prodPrice * (1 - discountRate/100)

print(f"MRP: {prodPrice} and Sale Price: {finalPrice}")
