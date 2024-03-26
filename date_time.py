from datetime import datetime, timedelta, UTC
import asyncio
import settings
import database as db

def find_due(type):
    day = datetime.utcnow().day
    month = datetime.utcnow().month
    year = datetime.utcnow().year

    next_day = datetime(year, month, day+1)
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if next_month == 1 else year

    if type == 'daily': 
        due_date = next_day - timedelta(seconds=1)
    elif type == 'weekly': 
        due_date =  next_day + timedelta(days=(7-next_day.weekday())) - timedelta(seconds = 1)
    elif type == 'monthly':
        due_date = datetime(next_year, next_month, 1) - timedelta(seconds = 1)
    return str(due_date)

async def run_loop():
    logger = settings.logging.getLogger("bot")
    while True:
        
        h = datetime.utcnow().hour
        m = datetime.utcnow().minute
        s = datetime.utcnow().second
        total_seconds = ((24-h)*3600)+((60-m)*60)+(60-s)

        logger.info(f"{total_seconds} seconds till entry update")
        await asyncio.sleep(total_seconds)

        db.update_streaks()
        print("updated streaks")
        db.update_entries()
        print("updated entries")