import matplotlib.pyplot as plt


quarters = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025', 'Q2 2025']
deliveries = [386810, 443956, 435059, 484507, 336681, 384122]


width = 0.2

fig, ax = plt.subplots()

ax.plot(quarters, deliveries, label='Tesla Sale Amount',)

ax.set_title('Tesla Sales')
ax.set_ylabel('Total Sales (Vehicles)')
ax.set_xlabel('Quarters')
ax.legend()  

plt.show()
