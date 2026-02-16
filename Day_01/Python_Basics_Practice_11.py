# You are preparing backend logic for a Flask API that accepts marks, calculates grade and returns result. 
def generate_report(*marks: int):
    sum = 0
    count = 0
    for mark in marks:
       sum += mark
       count += 1 

    final_marks = sum/count
    if final_marks>90 and final_marks<=100:
        return "A", final_marks
    elif final_marks>80 and final_marks<=90:
        return "B", final_marks
    elif final_marks>70 and final_marks<=80:
        return "C", final_marks
    elif final_marks>60 and final_marks<=70:
        return "D", final_marks
    elif final_marks>50 and final_marks<=60:
        return "E", final_marks
    else:
        return "F", final_marks
    

grade, percentage = generate_report(89,76,98,45,99)
print(f"Your grade is {grade}, with {percentage}%")


# DEsign backend logic for a login API that accepts a username and password, validates it and returns success or failiure.
def user_verification(username, password):
    valid_users = {"admin":"1234"}
    if username in valid_users:
        if password == valid_users[username]:
            return "success"
        else:
            return "failure! invalid password"
    else:
        return "failure! invalid username"
    

print(user_verification("admin", "1234"))
