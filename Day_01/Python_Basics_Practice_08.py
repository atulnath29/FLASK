# Create a User Class with attributes and a method to diplay details.
class User:
    def __init__(self, username, email, role):
        self.__username = username
        self.__email = email
        self.__role = role

    def display(self):
        return f"NAME: {self.__username}\nROLE: {self.__role}\nEMAIL: {self.__email}\n"
    
user = User("Babloo Ji","babloo69@email.com","operator")
print(user.display())

# Create a product class and calculate discounted price using a method. 
class Product:
    __discount = 0.30
    def __init__(self, pname, price):
        self.__pname = pname
        self.__price = price

    def discounted_price(self):
        return f"PRODUCT NAME: {self.__pname}\nMRP: {self.__price}\nDISCOUNTED PRICE: {self.__price*(1-self.__discount)}\n"
    
oreo = Product("Oreo",10)
print(oreo.discounted_price())
