

menu = {'Pizza': 3.00,
        'Nachos': 2.00,
        'Popcorn': 2.00,
        'Fries': 1.50,
        'Chips': 2.00,
        'Pretzel': 1.50,
        'Soda': 2.50,
        'Lemonade': 2.50,}

cart =[]
total = 0

print('----------MENU----------')

for key, value in menu.items():
    print(f'{key:10}: ${value:.2f}')

print('------------------------')

while True:
    food = input('Select an item (q to quit): ')
    if food == 'q':
        break
    elif menu.get(food) is not None:
        cart.append(food)

print('------------------------')

for food in cart:
    total = total + menu.get(food)
    print(food, end=' ')


currency={'Yen': 162.49,
          'Euro': 0.87,
          'Pound': 0.74}

type = input('Choose a currency (Yen, Euro, Pound, Dollar)')

if type == 'Dollar':
    total = total
if type == 'Yen':
    total = total * currency["Yen"]
elif type == 'Euro':
    total = total * currency["Euro"]
elif type == 'Pound':
    total = total * currency["Pound"]


print()
print(f'Total: {total:.2f}')