class character:  # Define the class
    def __init__(self, health, speed, damage, accuracy):  # Always use the __init__() funtion to set the parameters
        self.health = health  # Assign Variables
        self.speed = speed
        self.damage = damage
        self.accuracy = accuracy

    def Smash(self):
        self.damage += 75

    def Ninja(self):
        self.speed += 75

    def Health(self):
        self.health += 75

    def Accuracy(self):
        self.accuracy += 75

    def __str__(self):
        return f"Health: {self.health}, Speed: {self.speed}, Damage: {self.damage}, Accuracy: {self.accuracy}"


Smasher = character(25, 10, 100, 25)
Velocity = character(75, 100, 75, 80)
Vitality = character(100, 25, 50, 50)
Precision = character(50, 50, 75, 100)

input1 = input("Which character do you want? (Smasher, Velocity, Vitality, Precision): ")

if input1 == "Smasher":
    wc = Smasher
elif input1 == "Velocity":
    wc = Velocity
elif input1 == "Vitality":
    wc = Vitality
elif input1 == "Precision":
    wc = Precision
else:
    print("Invalid character choice!")
    wc = None

input2 = input("Choose a powerup: Smash, Ninja, Health, Accuracy. If none type 'None'")
if input2 == "Smash":
    wc.Smash()
    print(wc)
elif input2 == "Ninja":
    wc.Ninja()
    print(wc)
elif input2 == "Health":
    wc.Health()
    print(wc)
elif input2 == "Accuracy":
    wc.Accuracy()
    print(wc)
else:
    print("Invalid powerup choice!")
    wc = None