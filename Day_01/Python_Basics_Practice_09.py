# Create a base class User and a child class Admin that adds extra permissions.
class User:
    def __init__(self, name, mob):
        self._name = name
        self._mob = mob
        self._permissions = ["read", "search"]
    
    def show_permission(self):
        return f"{self._name} has {self._permissions} permissions"


class Admin(User):
    def __init__(self, name, mob):
        super().__init__(name, mob)
        self._permissions.append("editor")

    def show_permission(self):
        return f"{self._name} has {self._permissions} permissions"

user = User("babu", 12345678)
admin = Admin("raju",12345678)

print(user.show_permission())
print(admin.show_permission())


# A base class Employee is extented by Manager with additional responsibilities.
class Employee:
    def __init__(self, name, mob):
        self._name = name
        self._mob = mob
        self._responsibility = ["Task completion", "Accept task"]
    
    def show(self):
        return f"{self._name} has {self._responsibility} permissions"


class Manager(Employee):
    def __init__(self, name, mob):
        super().__init__(name, mob)
        self._responsibility.append("Assign task")

    def show(self):
        return f"{self._name} has {self._responsibility} permissions"

e = Employee("babu", 12345678)
m = Manager("raju",12345678)

print(e.show())
print(m.show())
