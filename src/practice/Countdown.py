from datetime import datetime
import time
from IPython.display import clear_output

birthday_month = 8
birthday_day = 22
while True:
    now = datetime.now()
    current_year = now.year
    birthday = datetime(year=current_year, month=birthday_month, day=birthday_day)

    if birthday < now:
        birthday = datetime(year=current_year + 1, month=birthday_month, day=birthday_day)

    time_left = birthday - now
    total_seconds = time_left.total_seconds()
    days = time_left.days
    hours = int((total_seconds % 86400) // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int((total_seconds - int(total_seconds)) * 1000)

    clear_output(wait=True)
    print("Countdown to your birthday")
    print(
        f'{days} days, {hours:02d} hours, {minutes:02d} minutes, {seconds:02d} seconds, {milliseconds:03d} milliseconds left!')
    time.sleep(0.001)