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
from time import gmtime, strftime, time
from discord.ext import commands

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

con = sqlite3.connect('db.db')  # open the database
cur = con.cursor()  # cursor object for the db

for row in cur.execute('select * from systemconfig'):
    selectedtz = timezone(row[0])

fmt = '%Y-%m-%d %H:%M:%S %Z%z'
timef = '%H:%M:%S'
datef = '%Y-%m-%d'


class reminders(commands.Cog, name="reminders"):
    def __init__(self, bot):
        self.bot = bot

    def time_name_convert(self, timestr, colon=True):
        hours = timestr[:2]
        if colon is True:
            minutes = timestr[3:5]
        else:
            minutes = timestr[2:4]

        if int(hours) > 00 and int(minutes) == 00:
            return "{} hours".format(hours)
        elif int(hours) == 00 and int(minutes) > 00:
            return "{} minutes".format(minutes)
        else:
            return "{} hours and {} minutes".format(hours, minutes)

    @commands.command(name="manage_consent")
    async def manage_consent(self, context, *args):
        """
        Manages consent for reminders
        """
        try:
            # explicit conversion otherwise it sometimes breaks
            value = int(args[0])
        except:
            print(
                "User passed in something that is not an int: {}".format(args[0],))
        if not args:
            await context.send("Syntax: $manage_consent ConsentValue\nE.g. $manage_consent 3\n\nConsent values: 0 - no reminders, 1 - dm reminders, 2 - channel reminders, 3 - both reminders")
        elif value < 0 or value > 3:
            await context.send("Consent values: 0 - no reminders, 1 - dm reminders, 2 - channel reminders, 3 - both reminders")
        else:
            looprun = "False"
            for row in cur.execute('select * from reminder_consent where username = ?', (context.message.author.id,)):
                looprun = "True"
                cur.execute('update reminder_consent set consent_value = ? where username = ?',
                            (value, context.message.author.id))
                await context.send("Consent value updated to {}".format(value))
            if looprun == "False":
                cur.execute('insert into reminder_consent values (?, ?)',
                            (context.message.author.id, value))
                await context.send("Consent value updated to {}".format(value))
            con.commit()

    @commands.command(name="remind_me")
    async def remind_me(self, context, *args):
        """
        Sets a reminder for an event
        """
        # players role id 835592255045500958
        # consent values: 0 - no reminders, 1 - dm reminders, 2 - channel reminders, 3 - both reminders
        # default value 2 for role reminders
        looprun = "False"
        crowlooprun = "False"
        if not args:
            await context.send("Syntax: $remind_me EventName HH:MM in 24hr format\nE.g. $remind_me Event1 01:30 will remind you 1.5hrs before the event")
        else:
            for crow in cur.execute('select consent_value from reminder_consent where username = ?', (context.message.author.id,)):
                crowlooprun = "True"
                if crow[0] != 0:
                    for row in cur.execute('select * from sessions where session_name = ?', (args[0],)):
                        looprun = "True"
                        strtime = args[1].replace(':', '')
                        cur.execute('insert into personal_reminders values (?, ?, NULL, ?)',
                                    (args[0], context.message.author.id, strtime))
                        con.commit()
                        await context.send("You will be reminded {} before the event!".format(self.time_name_convert(args[1], True)))
                else:
                    await context.send("You have opted out of all reminders, so no reminder was scheduled")
            if crowlooprun == "False":
                cur.execute('insert into reminder_consent values (?, 3)',
                            (context.message.author.id,))
                con.commit()
                await context.send("You had no consent on record for notifications\nBy default, your consent was recorded for both DM and channel reminders\n\nPlease re-run the reminder command")
            if looprun == "False" and crowlooprun != "False":
                await context.send("No such event found")

    @commands.command(name="show_reminders")
    async def shows_reminders(self, context):
        """
        Show scheduled reminders
        """
        counter = 1
        looprun = "False"
        for row in cur.execute('select * from personal_reminders where remind_who = ?', (context.message.author.id,)):
            looprun = "True"
            await context.send("{}. Event name: {}, Reminder time: {}".format(counter, row[0], self.time_name_convert(row[3], False)))
            counter += 1
        if looprun == "False":
            await context.send("No reminders found, sorry")

    @commands.command(name="remove_reminder")
    async def remove_reminder(self, context, *args):
        """
        Removes a reminder
        """
        if not args:
            await context.send("Syntax: $remove_reminder EventName\nE.g. $remove_reminder Event1\n\nYou can specify multiple events to remove reminders for")
        else:
            looprun = "False"
            counter = 1
            # nested for loops ftw
            for event in args:
                for row in cur.execute('select * from personal_reminders where session_name = ? and remind_who = ?', (event, context.message.author.id)):
                    looprun = "True"
                    cur.execute('delete from personal_reminders where session_name = ? and remind_who = ?', (
                        event, context.message.author.id))
                    await context.send("{}. Reminders for {} removed!".format(counter, event))
                    counter += 1
                if looprun == "False":
                    await context.send("No reminders found for {}!".format(event))
            con.commit()


def setup(bot):
    bot.add_cog(reminders(bot))
