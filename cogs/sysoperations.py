""""
Copyright © Krypton 2021 - https://github.com/kkrypt0nn
Description:
This is a template to create your own discord bot in python.

Version: 2.7
"""

import json
import os
import sys
import sqlite3
import discord
import asyncio
import subprocess
from discord.ext import commands

# Only if you want to use variables that are in the config.json file.
if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

con = sqlite3.connect('db.db') #open the database
cur = con.cursor() #cursor object for the db

# Here we name the cog and create a new class for the cog.
class SystemOperations(commands.Cog, name="operations"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="return_db")
    @commands.has_role(873031116179800065)
    async def return_db(self, context):
        """
        Returns the database schema
        """
        if config['debug_mode'] == True:
            for row in cur.execute('select * from sqlite_master'):
                await context.send(row)
        else:
            await context.send("Debug mode is not enabled!")

    @commands.command(name="get_conf")
    @commands.has_role(873031116179800065)
    async def get_conf(self, context):
        """
        Returns bot configuration from systemconfig table
        """
        if config['debug_mode'] == True:
            for row in cur.execute('select * from systemconfig'):
                if row[1] == 1:
                    dbgmode = "True"
                else:
                    dbgmode = "False"
                await context.send("*Stored configuration*\n-------------------------\nTimezone: {}\nDebug mode: {}".format(row[0], dbgmode))
        else:
            await context.send("Debug mode is not enabled!")

    @commands.command(name="dm_debug")
    @commands.has_role(873031116179800065)
    async def dm(self, ctx, *, message=None):
        """
        Sends a DM to the person using the command
        """
        message = message or "If you see this, the DM API works"
        await ctx.message.author.send(message)

    @commands.command(name="sysmem")
    @commands.has_role(873031116179800065)
    async def sysmem(self, context):
        """
        Returns system memory usage
        """
        await context.send(f"Memory :{psutil.virtual_memory()}")

    @commands.command(name="purge_msgs")
    @commands.has_role(873031116179800065)
    async def purge_msgs(self, ctx, amount:int, *, arg:str=None):
        """
        Purges channel messages (up to a 100 at a time)
        """
        msg = []
        channel = ctx.message.channel.history(limit=None)
        async for message in channel:
            if len(msg) <= amount:
                msg.append(message)
            else:
                pass
        await ctx.message.channel.delete_messages(msg)
        await asyncio.sleep(.5)
        botMessage = await ctx.send(f'**{amount}** messages were successfully deleted!')
        await asyncio.sleep(.5)
        await botMessage.delete()

    @commands.command(name="exec_sql")
    @commands.has_role(873031116179800065)
    async def exec_sql(self, context, *, arg):
        """
        Executes raw sql statements on the database
        """
        if config['debug_mode'] == True:
            await context.send("```diff\n-Use this with extreme caution! This executes raw SQL without any safeguards```")
            for row in cur.execute(arg):
                con.commit()
                await context.send(row)
        else:
            await context.send("Debug mode is not enabled!")

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(SystemOperations(bot))
