
passcode1 = 8920
passcode2 = 6740

input1 = int(input("Enter the passcode"))


if passcode1 == input1:
    print("Authorized")
    input2 = int(input("Enter the passcode"))
    if passcode2 == input2:
        print("Authorized")
        print("http://127.0.0.1:5500/hyperlinks.html")
    else:
        print("Invalid")
else:
    print("Invalid")