# Scenario 01
# Create a function that calculates GST for a bil amount and returns the final price.
def GST(bill_amount):
    return bill_amount*(1+18/100)

bill_amount = float(input("Enter bill amount: "))
print(f"BILL AMOUNT: {bill_amount}\nWITH GST: {GST(bill_amount)}\n")

# Scenario 02
# In a banking application, write a function to check whether a user has sufficient funds before withdrawal.
def check_funds(amount):
    balance = 1000
    if(amount<balance-500):
        print(f"Withdarwn {amount} and balance {balance-amount}\n")
    else:
        print("Insufficient funds\n")

amount = float(input("Enter amount: "))
check_funds(amount)
