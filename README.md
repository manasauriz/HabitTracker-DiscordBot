# Habit Tracker-Discord Bot.

## Introduction
This Discord bot helps users track their daily, weekly, and monthly habits right within their Discord server. Developed using Python and the discord.py library, the bot offers features such as habit tracking using dashboards, comparing progress using leaderboard, streaks, and XP rewards.

## Installation
1. Clone this repository to your local machine.
2. Install python, then install the required dependencies using pip:
   ```
   pip install -r requirements.txt
   ```
3. Edit the .env file in the project directory and add your Discord bot token:
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   ```
4. Move to the cloned directory and run the bot using the following command:
   ```
   python bot.py
   ```

## Commands
After inviting the bot to your server, you can interact with it using the following commands:
> !join - Join the community and start habit tracking

> !leave - Leave the community and stop habit tracking

> !add <habit> - Add a habit to your dashboard

> !remove <ID> - Remove a habit from your dashboard

> !complete <ID> - Mark a habit as completed

> !profile - Display your habit profile

> !dashboard - Display a dashboard of your habits

> !leaderboard - Display leaderboard for your server

## Screenshots

### Habit Dashboard
![Habit Dashboard](https://i.ibb.co/DfdRRYd/db.png)

### Habit Profile
![Habit Profile](https://i.ibb.co/PFHtGCk/profile.png)

### Habit Leaderboard
![Habit Leaderboard](https://i.ibb.co/28kmXFL/leaderboard.png)
