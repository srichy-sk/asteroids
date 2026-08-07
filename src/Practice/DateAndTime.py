import datetime


today = datetime.date.today()
print(f' The date today is {today}')

now = datetime.datetime.now()
print(f' The date is first and the time is second {now}')
now = now.strftime(" The time is %H:%M:%S and the date is %m/%d/%Y")

print(now)