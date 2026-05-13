import matplotlib.pyplot as plt


def autolabel(rectangle_group):
    for rect in rectangle_group:
        height = rect.get_height()  
        ax.annotate(str(height),
            xy=(rect.get_x() + rect.get_width() / 2, height),
            ha = 'center',
            xytext=(0,3), textcoords='offset points')  

phases = ['Mid 90s', 'Early 2k', 'Mid 2k', 'Mid 2010s']

playstation = [102, 155, 87, 110]
xbox = [0, 24, 86, 50]
nintendo = [33, 22, 102, 62]
pc_sales = [71, 128, 240, 316]

width = 0.2

x_playstation = [x - width for x in range(len(playstation))]
x_xbox = [x for x in range(len(xbox))]
x_nintendo = [x + width for x in range(len(nintendo))]

fig, ax = plt.subplots()

rect1 = ax.bar(x_playstation, playstation, width, label='PlayStation')
rect2 = ax.bar(x_xbox, xbox, width, label='Xbox')
rect3 = ax.bar(x_nintendo, nintendo, width, label='Nintendo')
ax.plot(phases, pc_sales, label='PC Sales',)

ax.set_title('Console and PC Sales')
ax.set_ylabel('Total Sales (In Millions)')
ax.legend()  

autolabel(rect1)
autolabel(rect2)
autolabel(rect3)
plt.show()
