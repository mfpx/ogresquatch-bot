""""
Copyright © Krypton 2021 - https://github.com/kkrypt0nn
Description:
This is a template to create your own discord bot in python.

Version: 2.7
"""

import json
import os
import platform
import random
import sys
import aiohttp
import discord
import pytz
import sqlite3
from pytz import timezone
import pytz.exceptions
from datetime import datetime, timedelta
from time import gmtime, strftime, time, sleep, perf_counter
import threading
import schedule
from discord.ext import commands

if not os.path.isfile("config.json"):
    #sys.exit("'config.json' not found! Please add it and try again.")
    print("config.json not found")
else:
    with open("config.json") as file:
        config = json.load(file)

con = sqlite3.connect('db.db') #open the database
cur = con.cursor() #cursor object for the db

for row in cur.execute('select * from systemconfig'):
    selectedtz = timezone(row[0])

fmt = '%Y-%m-%d %H:%M:%S %Z%z'
timef = '%H:%M:%S'
datef = '%Y-%m-%d'

class cron(commands.Cog, name="cron"):
    def __init__(self, bot, *args, **kwargs):
        self.bot = bot

    @comands.command(name="threading")
    async def start_thread(self, context):
        pass
        #bruh

def setup(bot):
    bot.add_cog(cron(bot))
