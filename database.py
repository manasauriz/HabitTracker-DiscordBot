import sqlite3
import date_time as dt

con = sqlite3.connect('bot.sqlite')
cur = con.cursor()

def create_tables():
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS Users(
                  user_id INTEGER PRIMARY KEY,
                  username TEXT UNIQUE,
                  xp_value INTEGER,
                  league TEXT CHECK (league IN ('novice','silver','gold','platinum','diamond')),
                  rank INTEGER
    );
    CREATE TABLE IF NOT EXISTS Habits(
                habit_id INTEGER PRIMARY KEY,
                habit TEXT,
                user_id INTEGER REFERENCES Users(user_id),
                type TEXT CHECK (type IN ('daily','weekly','monthly')),
                streak INTEGER      
    );
    CREATE TABLE IF NOT EXISTS Entries(
                  entry_id INTEGER PRIMARY KEY,
                  habit_id INTEGER REFERENCES Habits(habit_id),
                  due_date TEXT,
                  status INTEGER
    )
    ''')

def clear_tables():
    cur.executescript('''
        DELETE FROM Entries;
        DELETE FROM Habits;
        DELETE FROM Users
    ''')
    con.commit()

def check_user(username):
    users = cur.execute('SELECT username FROM Users')
    for user in users:
        if username == user[0]: return True
    return False

def join_user(username):
    cur.execute('INSERT INTO Users(username, xp_value, league) VALUES (?,?,?)', (username,0,"novice"))
    try:
        rank = cur.execute('''SELECT rank FROM Users WHERE username != (?)
                           ORDER BY rank DESC''', (username,)).fetchone()[0] + 1
    except:
        rank = 1
    cur.execute('''UPDATE Users SET rank = (?)
                WHERE username = (?)''', (rank,username))
    con.commit()

def leave_user(username):
    user_id = cur.execute('''SELECT (user_id) FROM Users 
                          WHERE username = (?)''', (username,)).fetchone()[0]

    user_habits = cur.execute('''SELECT (habit_id) FROM Habits 
                           WHERE user_id = (?)''', (user_id,)).fetchall()
    for entry in user_habits:
        habit_id = entry[0]
        cur.execute('DELETE FROM Entries WHERE habit_id = (?)', (habit_id,))

    cur.execute('DELETE FROM Habits WHERE user_id = (?)', (user_id,))
    cur.execute('DELETE FROM Users WHERE username = (?)', (username,))
    con.commit()

def check_habit(username, given_habit):
    user_id = cur.execute('''SELECT (user_id) FROM Users 
                          WHERE username = (?)''', (username,)).fetchone()[0]
    habits = cur.execute('SELECT habit FROM Habits WHERE user_id = (?)', (user_id,)).fetchall()
    for habit in habits:
        if given_habit == habit[0]: return False
    return True

def add_habit(habit, username, type):
    user_id = cur.execute('''SELECT (user_id) FROM Users 
                          WHERE username = (?)''', (username,)).fetchone()[0]

    cur.execute('''INSERT INTO Habits(habit, user_id, type, streak) 
                VALUES (?,?,?,?)''',(habit,user_id,type,0))
    habit_id = cur.execute('''SELECT (habit_id) FROM Habits 
                           WHERE user_id = (?) AND habit = (?)''', (user_id, habit)).fetchone()[0]

    due_date = dt.find_due(type)
    cur.execute('''INSERT INTO Entries(habit_id, due_date, status) 
                VALUES (?,?,?)''', (habit_id,due_date,0))
    con.commit()

def remove_habit(number, username):
    habit_id = habit_list(username)[number]['habit_id']

    cur.execute('DELETE FROM Entries WHERE habit_id = (?)', (habit_id,))
    cur.execute('DELETE FROM Habits WHERE habit_id = (?)', (habit_id,))
    con.commit()

def user_list():
    count = 1
    user_list = dict()
    cur.execute('''SELECT * FROM Users ORDER BY rank ASC''')

    for user in cur:
        inner_dict = {'user_id':user[0],
                      'username':user[1],
                      'xp_value':user[2],
                      'league':user[3],
                      'rank':user[4]}
        
        user_list[count] = user_list.get(count, inner_dict)
        count += 1
    con.commit()
    return user_list

def habit_list(username):
    count = 1
    habit_list = dict()
    cur.execute('''SELECT * FROM Entries 
                    JOIN Habits ON Entries.habit_id = Habits.habit_id 
                    JOIN Users ON Habits.user_id = Users.user_id 
                    WHERE Users.username = (?) AND Entries.due_date > (?)
                    ORDER BY Habits.habit_id''', (username,str(dt.datetime.utcnow())))
    
    for habit in cur:
        inner_dict = {'entry_id':habit[0], 
                  'due_date':habit[2], 
                  'status':habit[3], 
                  'habit_id':habit[4], 
                  'habit':habit[5], 
                  'type':habit[7],
                  'streak':habit[8]}

        habit_list[count] = habit_list.get(count, inner_dict)
        count += 1
    con.commit()
    return habit_list

def update_entries():
    all_habits = cur.execute('SELECT habit_id from Habits').fetchall()

    for habit in all_habits:
        habit_id = habit[0]
        entry = cur.execute('''
            SELECT * FROM Entries
            JOIN Habits ON Entries.habit_id = Habits.habit_id
            WHERE Habits.habit_id = (?)
            ORDER BY Entries.entry_id DESC
            ''', (habit_id,)).fetchone()
        prev_date = entry[2]
        type = entry[7]

        if str(dt.datetime.utcnow()) > prev_date:
            next_date = dt.find_due(type)
            cur.execute('''INSERT INTO Entries(habit_id, due_date, status) 
                        VALUES (?,?,?)''', (habit_id,next_date,0))
            con.commit()

def update_streaks():
    all_habits = cur.execute('SELECT habit_id from Habits').fetchall()

    for habit in all_habits:
        habit_id = habit[0]
        entry = cur.execute('''
            SELECT * FROM Entries
            JOIN Habits ON Entries.habit_id = Habits.habit_id
            WHERE Habits.habit_id = (?)
            ORDER BY Entries.entry_id DESC
            ''', (habit_id,)).fetchone()

        if entry[3] == 0:
            cur.execute('''UPDATE Habits SET streak = (?)
                        WHERE habit_id = (?)''', (0,habit_id))
            con.commit()

def update_status(entry):
    entry_id = entry['entry_id']
    cur.execute('UPDATE Entries SET status = (?) WHERE entry_id = (?)', (1,entry_id))
    con.commit()

def get_xp(username):
    xp_value = cur.execute('''SELECT xp_value FROM Users 
                           WHERE username = (?)''', (username,)).fetchone()[0]
    return xp_value

def get_league(username):
    league = cur.execute('''SELECT league FROM Users 
                           WHERE username = (?)''', (username,)).fetchone()[0]
    return league

def update_league(username, value):
    cur.execute('''UPDATE Users SET league = (?)
                WHERE username = (?)''', (value,username))
    con.commit()
    
def update_streak(habit_id, value):
    cur.execute('''UPDATE Habits SET streak = (?)
                WHERE habit_id = (?)''', (value,habit_id))
    con.commit()

def get_rank(username):
    rank = cur.execute('''SELECT rank FROM Users 
                           WHERE username = (?)''', (username,)).fetchone()[0]
    return rank

def update_user(username, xp):
    cur.execute('''UPDATE Users SET xp_value = (?)
                WHERE username = (?)''', (xp,username))
    con.commit()
    rank = get_rank(username)
    data = user_list()
    count = 0

    for id, entry in data.items():
        if entry['username'] == username: continue
        if xp >= entry['xp_value'] and rank < entry['rank']: continue
        if xp < entry['xp_value'] and rank > entry['rank']: continue

        if xp >= entry['xp_value'] and rank > entry['rank']:
            cur.execute('''UPDATE Users SET rank = (?)
                        WHERE user_id = (?)''', (entry['rank']+1,entry['user_id']))
            count += 1
        
        if xp < entry['xp_value'] and rank < entry['rank']:
            cur.execute('''UPDATE Users SET rank = (?)
                        WHERE user_id = (?)''', (entry['rank']-1,entry['user_id']))
            count -= 1
    
    cur.execute('UPDATE Users SET rank = (?) WHERE username = (?)', (rank-count,username))
    con.commit()