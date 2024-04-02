import settings
import discord
from discord.ext import commands
import database as db
import date_time as dt
import gamification as game

def run_bot():
    logger = settings.logging.getLogger("bot")
    db.create_tables()

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = commands.Bot(command_prefix='!', intents=intents)

    global not_found
    not_found =  f'```\nUser: not found.\n'
    not_found += f'Use !join to initiate yourself!\n```'

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")
        bot.loop.create_task(dt.run_loop())

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            syntax_err = f"```\nERROR: Invalid Syntax\n"
            syntax_err += f"Use <!help {ctx.command.name}> to get the proper syntax.\n```"
            await ctx.send(syntax_err)

        elif isinstance(error, commands.CommandNotFound):
            err_msg = f"```\nERROR: Command not found\n"
            err_msg += f"Use <!help> to see available commands.\n```"
            await ctx.send(err_msg)

        elif isinstance(error, commands.BadArgument):
            syntax_err = f"```\nERROR: Invalid Syntax\n"
            syntax_err += f"Use <!help {ctx.command.name}> to get the proper syntax.\n```"
            await ctx.send(syntax_err)
        
        elif isinstance(error, commands.CommandError):
            print(error)

    @bot.command(
            description = '''Join the community to start tracking your habits.
            Initiate yourself to the bot.''',
            brief = "Join the community and start habit tracking",
    )
    async def join(ctx):
        username = ctx.author.name

        if db.check_user(username):
            msg = f'```\nYou have already joined!\n'
            msg += f'Use !dashboard to view your habits.\n```'
            await ctx.send(msg)
        else:
            db.join_user(username)
            await ctx.send(f'```\nYou have been initiated!\n```')
    
    @bot.command(
            description = '''Leave the community to stop tracking your habits.
            Delete all your data from the bot.''',
            brief = "Leave the community and stop habit tracking",
    )
    async def leave(ctx):
        username = ctx.author.name

        if db.check_user(username): 
            db.leave_user(username)
            await ctx.send(f'```\nYou have been removed. Sad to see you go :(\n```')  
        else: await ctx.send(not_found)
    
    @bot.command(
            aliases = ['a'],
            help = "!add <habit> \n-OR- \n!a <habit>",
            description = '''Use this command to add a new habit to your dashboard. 
            Make sure to include any one of these keywords in your habit name: 
            'daily': Habit repeats every day.
            'weekly': Habit repeats every week at the end of the week.
            'monthly': Habit repeats every month at the end of the month.
            Syntax given below''',
            brief = "Add a habit to your dashboard",
    )
    async def add(ctx, *, habit):
        username = ctx.author.name

        if db.check_user(username):
            if db.check_habit(username, habit):
                type = dt.find_type(habit)

                if type is None:
                    err_msg = f'```\nERROR: Invalid Input\n'
                    err_msg += f"Must include the keywords: 'daily', 'weekly' or 'monthly'\n```"
                    await ctx.send(err_msg)
                else:
                    db.add_habit(habit, username, type)
                    game.add_xp(username, 50)

                    add_msg = f'```\n"{habit}" has been added to your dashboard successfully!\n'
                    add_msg += f'You gained 50 XP\n```'
                    await ctx.send(add_msg)

                    league = game.check_league(username)
                    if league:
                        l_msg = f'```\nCongratulations! You have levelled up\n'
                        l_msg += f'Welcome to the {league.capitalize()} league!\n```'
                        await ctx.send(l_msg)
            else: await ctx.send(f"```\nERROR: Habit already found in {username}'s database.\n```")
        else: await ctx.send(not_found)

    @bot.command(
            aliases = ['r'],
            help = "!remove <ID>\n-OR- \n!r <ID>",
            description = '''Use this command to remove a habit from your dashboard. 
            Use !dashboard to get the ID corresponding to the habit. Syntax given below''',
            brief = "Remove a habit from your dashboard",
    )
    async def remove(ctx, id: int):
        username = ctx.author.name

        if db.check_user(username):
            db.remove_habit(id, username)
            remove_msg = f'```\nHabit ID {id} has been removed!\n```'
            await ctx.send(remove_msg)
        else: await ctx.send(not_found)
        
    @bot.command(
            aliases = ['c'],
            help = "!complete <ID>\n-OR- \n!c <ID>",
            description = '''Use this command to mark a habit as completed. 
            Use !dashboard to get the ID corresponding to the habit. Syntax given below''',
            brief = "Mark a habit as completed",
    )
    async def complete(ctx, id: int):
        username = ctx.author.name

        if db.check_user(username):
            entry = db.habit_list(username)
            complete_msg = f'```\n'
            
            status = entry[id]['status']
            habit_id = entry[id]['habit_id']
            streak = 1 + entry[id]['streak']

            if  status == 1: 
                complete_msg += f'Habit ID {id} has already been completed!\n```'
                await ctx.send(complete_msg)
            else:
                db.update_status(entry[id])
                db.update_streak(habit_id, streak)
                complete_msg += f'Good job on completing your habit!\n'

                if len(entry) >= 10:
                    xp = 25
                elif len(entry) >= 8:
                    xp = 30
                elif len(entry) >= 5:
                    xp = 40
                elif len(entry) >= 3:
                    xp = 45
                else: xp = 50

                if streak % 10 == 0:
                    xp += 100
                    complete_msg += f'Woohoo! A {streak} day streak on this habit. Have some extra XP'

                game.add_xp(username, xp)
                complete_msg += f'You have been awarded {xp} XP\n```'
                await ctx.send(complete_msg)

                league = game.check_league(username)
                if league:
                    l_msg = f'```\nCongratulations! You have levelled up\n'
                    l_msg += f'Welcome to the {league.capitalize()} league!\n```'
                    await ctx.send(l_msg)
            
        else: await ctx.send(not_found)
    
    @bot.command(
            aliases = ['p'],
            help = "!profile \n-OR- \n!p",
            description = '''Use this command to display and overview of your habit profile.
            View your XP, League and other stats''',
            brief = "Display your habit profile"
    )
    async def profile(ctx):
        username = ctx.author.name
        name = ctx.author.display_name

        if db.check_user(username):
            xp = db.get_xp(username)
            league = db.get_league(username)
            rank = db.get_rank(username)

            embed = discord.Embed(
                title = f"{name}'s Habit Profile",
                description = f"Rank: {rank}",
                color = discord.Color.green()
            )
            embed.set_thumbnail(url=game.league_image(league))
            embed.add_field(name='XP Value', value=f'\U0001F31F {xp} XP')
            embed.add_field(name="League", value=f'\U0001F3C6 {league.capitalize()} League')

            progress_bar = game.progress_bar(xp)
            embed.add_field(name="Progress Bar", value=progress_bar, inline=False)
            await ctx.send(embed=embed)

        else: await ctx.send(not_found)

    @bot.command(
            aliases = ['db'],
            help = "!dashboard \n-OR- \n!db",
            description = '''Use this command to display a dashboard of your habits. 
            View the stats for each habit by using the buttons.''',
            brief = "Display a dashboard of your habits"
    )
    async def dashboard(ctx):
        username = ctx.author.name
        name = ctx.author.display_name
        avatar = ctx.author.avatar

        if db.check_user(username):
            user_habits = db.habit_list(username)
            dbp = 0

            embed = discord.Embed(
                title=f"{name}'s Habit Dashboard",
                description=f'Total Habits: {len(user_habits)}',
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=avatar)
            embed.add_field(name='Habit List', value=game.get_dashboard(username), inline=False)

            async def update_message(interaction: discord.Interaction, embed: discord.Embed, dbp: int):
                prev_button.disabled = dbp <= 1
                next_button.disabled = dbp >= len(user_habits)
                await interaction.message.edit(embed=embed, view=view)
                await interaction.response.defer()
            view = discord.ui.View()

            async def db_callback(interaction: discord.Interaction):
                nonlocal dbp
                dbp = 0
                await update_message(interaction, embed, dbp)

            db_button = discord.ui.Button(label="Dashboard", style=discord.ButtonStyle.primary)
            db_button.callback = db_callback
            view.add_item(db_button)

            async def prev_callback(interaction: discord.Interaction):
                nonlocal dbp
                dbp = max(1, dbp-1)
                await update_embed(interaction, dbp)

            prev_button = discord.ui.Button(label='\u2B05️', style=discord.ButtonStyle.secondary)
            prev_button.callback = prev_callback
            view.add_item(prev_button)

            async def next_callback(interaction: discord.Interaction):
                nonlocal dbp
                dbp = min(len(user_habits), dbp+1)
                await update_embed(interaction, dbp)

            next_button = discord.ui.Button(label='\u27A1️', style=discord.ButtonStyle.secondary)
            next_button.callback = next_callback
            view.add_item(next_button)

            async def update_embed(interaction: discord.Interaction, dbp: int):
                embed = discord.Embed(
                    title=f"{dbp}. {user_habits[dbp]['habit']}",
                    color=discord.Color.blue()
                )
                if user_habits[dbp]['status'] == 1:
                    entry_status = "\u2705 Completed"  
                else: entry_status = "\u274C Not Completed"
                embed.add_field(name='Status', value=entry_status, inline=False)

                date_object = dt.datetime.strptime(user_habits[dbp]['due_date'], '%Y-%m-%d %H:%M:%S')
                formatted_date = f"\u23F0 {date_object.strftime('%I:%M %p %d %B, %Y')}"
                embed.add_field(name='Due Date', value=formatted_date, inline=False)

                type = f"\U0001F504 {user_habits[dbp]['type'].capitalize()}"
                embed.add_field(name='Type', value=type, inline=False)

                streak = f"\U0001F525 {user_habits[dbp]['streak']} Days"
                embed.add_field(name='Streak', value=streak, inline=False)

                await update_message(interaction, embed, dbp)
            prev_button.disabled = True
            await ctx.send(embed=embed, view=view)

        else: await ctx.send(not_found)

    @bot.command(
            aliases = ['lb'],
            help = "!leaderboard \n-OR- \n!lb",
            description = '''Use this command to display the leaderboard for your server.
            View XP stats and league of all users.''',
            brief = "Display leaderboard for your server"
    )
    async def leaderboard(ctx):
        username = ctx.author.name

        if db.check_user(username):
            user_stats = db.user_list()
            lbp = 0

            user_xp = db.get_xp(username)
            user_league = db.get_league(username).capitalize()
            user_rank = db.get_rank(username)

            embed = discord.Embed(
                title=f"Habit Leaderboard",
                description=f"Total Users: {len(user_stats)}",
                color=discord.Color.green()
            )
            if len(user_stats) >= 1:
                user1 = user_stats[1]['username']
                xp1 = user_stats[1]['xp_value']
                league1 = user_stats[1]['league'].capitalize()
                val1 = f'```\n\U0001F947 {user1} |\U0001F31F {xp1} XP |\U0001F3C6 {league1} League\n```'
                embed.add_field(name='Rank 1', value=val1, inline=False)

            if len(user_stats) >= 2:
                user2 = user_stats[2]['username']
                xp2 = user_stats[2]['xp_value']
                league2 = user_stats[2]['league'].capitalize()
                val2 = f'```\n\U0001F948 {user2} |\U0001F31F {xp2} XP |\U0001F3C6 {league2} League\n```'
                embed.add_field(name='Rank 2', value=val2, inline=False)

            if len(user_stats) >= 3:
                user3 = user_stats[3]['username']
                xp3 = user_stats[3]['xp_value']
                league3 = user_stats[3]['league'].capitalize()
                val3 = f'```\n\U0001F949 {user3} |\U0001F31F {xp3} XP |\U0001F3C6 {league3} League\n```'
                embed.add_field(name='Rank 3', value=val3, inline=False)

            if user_rank > 3:
                lb_msg = f'```\n.\n.\n.\n\u2B50 {user_rank}. {username} |\U0001F31F {user_xp} XP |\U0001F3C6 {user_league} League\n```'
                embed.add_field(name='Your stats', value=lb_msg, inline=False)

            async def update_message(interaction: discord.Interaction, embed: discord.Embed, lbp: int):
                prev_button.disabled = lbp <= 1
                next_button.disabled = lbp >= (len(user_stats)//10)+1
                await interaction.message.edit(embed=embed, view=view)
                await interaction.response.defer()
            view = discord.ui.View()

            async def top_callback(interaction: discord.Interaction):
                nonlocal lbp
                lbp = 0
                await update_message(interaction, embed, lbp)

            top_button = discord.ui.Button(label='\U0001F3C6', style=discord.ButtonStyle.primary)
            top_button.callback = top_callback
            view.add_item(top_button)

            async def prev_callback(interaction: discord.Interaction):
                nonlocal lbp
                lbp = max(1, lbp-1)
                await update_embed(interaction, lbp)

            prev_button = discord.ui.Button(label='\u2B05️', style=discord.ButtonStyle.secondary)
            prev_button.callback = prev_callback
            view.add_item(prev_button)

            async def next_callback(interaction: discord.Interaction):
                nonlocal lbp
                lbp = min((len(user_stats)//10)+1, lbp+1)
                await update_embed(interaction, lbp)

            next_button = discord.ui.Button(label='\u27A1️', style=discord.ButtonStyle.secondary)
            next_button.callback = next_callback
            view.add_item(next_button)

            async def update_embed(interaction: discord.Interaction, lbp: int):
                embed = discord.Embed(
                    title='Habit Leaderboard',
                    color=discord.Color.green()
                )
                embed.add_field(name=f"Page {lbp}",value=game.get_leaderboard(lbp), inline=False)

                if user_rank > (lbp*10):
                    new_msg = f'```\n.\n.\n.\n\u2B50 {user_rank}. {username} |\U0001F31F {user_xp} XP |\U0001F3C6 {user_league} League\n```'
                    embed.add_field(name='Your stats', value=new_msg, inline=False)

                await update_message(interaction, embed, lbp)
            prev_button.disabled = True
            await ctx.send(embed=embed, view=view)
        
        else: await ctx.send(not_found)

    @bot.command(
            aliases = ['mt'],
            help = "!motivate \n-OR- \n!mt",
            description = '''Use this command to display a motivational quote!''',
            brief = "Display a motivational quote"
    )
    async def motivate(ctx):
        username = ctx.author.name

        if db.check_user(username):
            embed = discord.Embed(
                title=game.get_quote("quote"),
                description=game.get_quote("author"),
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

        else: await ctx.send(not_found)

    @bot.command(
            aliases = ['t'],
            description = "Command for testing purposes",
            enabled = True,
            hidden = True
    )
    async def test(ctx):
        await ctx.send('testing')
    
    bot.run(settings.DISCORD_API_TOKEN, root_logger=True)

if __name__ == "__main__":
    db.update_entries()
    run_bot()