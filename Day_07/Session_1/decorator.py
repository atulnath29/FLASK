def sistec(func):
    def wrapper(name):
        print("Welcome to Sistec")
        result = func(name)
        print("We are in Sistec")
        return result
    return wrapper
@sistec
def hello(name):
    return f"Hello, {name}!"

print(hello("flask"))