# Concession stand program

menu = {"pizza": 3.00,
               "nachos": 4.50,
               "popcorn": 6.00,
               "fries": 2.50,
               "chips": 1.00,
               "pretzel": 3.50,
               "soda": 3.00,
               "lemonade": 4.25}
cart = []
total1 = 0

print("--------- MENU ---------")
for key, value in menu.items():
    print(f"{key:10}: ${value:.2f}")
print("------------------------")

while True:
    food = input("Select an item (q to quit): ").lower()
    if food == "q":
        break
    elif menu.get(food) is not None:
        cart.append(food)

print("------ YOUR ORDER ------")
for food in cart:
    total1 += menu.get(food)
    print(food, end=" ")

print()
print(f"Total is: ${total1:.2f}")

print("-------- PAYMENT --------")
# Credit card validator program:

sum_odd_digits = 0
sum_even_digits = 0
total = 0

card_number = input("Enter your credit card number: ")
card_number = card_number.replace("-" , "")
card_number = card_number.replace(" " , "")
card_number = card_number[::-1]

for character in card_number[::2]:
    sum_odd_digits += int(character)

for x in card_number[1::2]:
    x = int(x) * 2
    if x >= 10:
        sum_even_digits  += (1 + (x % 10))
    else:
        sum_even_digits += x

total = sum_even_digits = sum_odd_digits

if total % 10 == 0:
    print("Your Credit Card is valid")
    print(f'{total1} has been collect from you Credit Card')
else:
    print("Your Credit Card is not valid please try again")
    card_number = input("Enter your credit card number: ")
