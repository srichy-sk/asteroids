import random

options = ("Rock", "Paper", "Scissors")
option2 = random.choice(options)
option1 = input("Enter a option: (Rock, Paper, Scissors): ")

print("Your Option: " + option1)
print("System Option: " + option2)

if option2 == "Scissors" and option1 == "Paper":
    print("You Lose")
elif option2 == "Rock" and option1 == "Scissors":
    print("You Lose")
elif option2 == "Paper" and option1 == "Rock":
    print("You Lose")
elif option1 == option2:
    print("Draw")
else:
    print("You Win")
