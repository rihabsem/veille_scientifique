from datetime import datetime, timedelta

date = datetime.now()
date_next = date + timedelta(days=31)
user_last_updated_date = date.strftime("%Y-%m-%d")
user_next_updated_date = date_next.strftime("%Y-%m-%d")
print(f"{user_last_updated_date} {user_next_updated_date}")