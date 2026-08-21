
number1 = float(input("Enter your first number: "))
operator = input("Enter an operator, + - * / **")
number2 = float(input("Enter your second number: "))

if operator == "+":
    result = number1 + number2
elif operator == "*":
    result = number1 * number2
elif operator == "/":
    result = number1 / number2
elif operator == "-":
    result = number1 - number2
elif operator == "**":
    result = number1 ** number2
else:
    print("This is not a valid operator or this calculator does not support this operator ")

print(f'The result is {result}')