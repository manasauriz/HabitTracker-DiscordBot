import database as db
import date_time as dt
import requests

emoji = '\U0000203E'

def league_image(league):
    if league == "novice": return "https://i.ibb.co/fCKYYFz/01-novice.png"
    if league == "silver": return "https://i.ibb.co/XDhhVd7/02-silver.png"
    if league == "gold": return "https://i.ibb.co/2ZDDDDH/03-gold.png"
    if league == "platinum": return "https://i.ibb.co/3BGk8Fn/04-platinum.png"
    if league == "diamond": return "https://i.ibb.co/NLTN3Ww/05-diamond.png"

def add_xp(username, value):
    prev_xp = db.get_xp(username)
    new_xp = prev_xp + value
    db.update_user(username, new_xp)

def find_league(value):
    if value < 2500:
        return "novice"
    elif value < 5000:
        return "silver"
    elif value < 7500:
        return "gold"
    elif value < 10000:
        return "platinum"
    else: return "diamond"
    
def check_league(username):
    value = db.get_xp(username)
    prev_league = db.get_league(username)
    new_league = find_league(value)

    if prev_league != new_league:
        db.update_league(username, new_league)
        return new_league
    else: return False

def progress_bar(xp):
    current_league = find_league(xp)
    next_league = find_league(xp+2500)

    if current_league == "novice": min_xp,max_xp = 0,2500
    elif current_league == "silver": min_xp,max_xp = 2500,5000
    elif current_league == "gold": min_xp,max_xp = 5000,7500
    elif current_league == "platinum": min_xp,max_xp = 7500,10000
    elif current_league == "diamond": return f'```\nNo more progress. You have made it!\n```'

    progressed_xp = xp - min_xp
    remaining_xp = max_xp - xp

    relative_pxp = progressed_xp//40
    relative_rxp = 40 - relative_pxp

    bar = f"```\n{min_xp:5}{' '*32}{max_xp:5}\n"
    bar += f" {'_'*40} \n"
    bar += f"|{'/'*relative_pxp}{' '*relative_rxp}|\n"
    bar += f' {emoji*40} \n'
    bar += f'XP needed to reach the {next_league.capitalize()} league: {remaining_xp}\n```'

    return bar

def get_dashboard(username):
    user_habits = db.habit_list(username)
    dashboard = f"```\n{'_'*42}\nID| Habit{' '*18} |Time Left|   \n{emoji*42}\n"

    for id, data in user_habits.items():
        due_date = dt.datetime.strptime(data['due_date'], "%Y-%m-%d %H:%M:%S")
        habit = data['habit'][:20] + '...' if len(data['habit']) > 23 else data['habit']
        difference = due_date - dt.datetime.utcnow()

        r_days = difference.days
        r_hrs = difference.seconds//3600
        r_mins = (difference.seconds//60)-((difference.seconds//3600)*60)

        if data['status'] == 1:
            status = '\u2705'
            r_time = f'    -    '
        elif data['type'] == 'daily':
            status = '\u274C'
            r_time = f" {r_hrs:2d}H {r_mins:2d}M "
        else:
            status = '\u274C'
            r_time = f" {r_days:2d}D {r_hrs:2d}H "
        
        dashboard += f'{id:2d}| {habit:<23} |{r_time}|{status}\n'
    dashboard += f'{emoji*42}\n```'
    return dashboard

def get_leaderboard(lbp):
    start = ((lbp - 1) * 10) + 1
    end = lbp * 10

    sliced_list = {k: v for k, v in db.user_list().items() if start <= k <= end}
    leaderboard = f"```\n{'_'*42}\nRank| Username{' '*8} |  XP  | League  \n{emoji*42}\n"

    for id, data in sliced_list.items():
        username = data['username'][:13] + '...' if len(data['username']) > 16 else data['username']
        league = data['league'].capitalize()
        leaderboard += f"{data['rank']:4d}| {username:<16} |{data['xp_value']:5d} | {league:9}\n"
    
    leaderboard += f'{emoji*42}\n```'
    return leaderboard

def get_quote(type):
    url = "https://api.quotable.io/quotes/random?tags=change|competition|failure|gratitude|inspirational|perseverance|success|work"
    response = requests.get(url)
    if response.status_code == 200:
        quote_data = response.json()[0]
        if type == "quote": 
            content = quote_data['content']
            return f'" {content} "'
        if type == "author": 
            content = quote_data['author']
            return f'~ {content}'
    else:
        return "Failed to fetch motivational quote."