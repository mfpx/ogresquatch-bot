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


class scheduler(commands.Cog, name="scheduler"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="get_td")
    async def get_td(self, ctx):
        """
        Returns localised time and date
        """
        global timef, datef, selectedtz
        utc = pytz.utc
        unix_epoch = time()
        utctime = utc.localize(datetime.utcfromtimestamp(int(unix_epoch)))
        convertedtime = utctime.astimezone(selectedtz)
        await ctx.send("Date is: {}\nTime is: {}".format(convertedtime.strftime(datef), convertedtime.strftime(timef)))

    @commands.command(name="get_tz")
    async def get_tz(self, ctx):
        """
        Returns the current timezone setting and its time offset
        """
        global selectedtz
        utc = pytz.utc
        unix_epoch = time()
        utctime = utc.localize(datetime.utcfromtimestamp(int(unix_epoch)))
        convertedtime = utctime.astimezone(selectedtz)
        timezone = selectedtz.zone
        offset = '%z'
        await ctx.send("Timezone is **{}** and the time offset is **{}**".format(timezone, convertedtime.strftime(offset)))

    @commands.command(name="set_tz")
    @commands.has_role(873031116179800065)
    async def set_tz(self, ctx, arg):
        """
        Changes the bot timezone
        """
        global datef, timef, selectedtz
        try:
            selectedtz = timezone(arg)
            utc = pytz.utc
            unix_epoch = time()
            utctime = utc.localize(datetime.utcfromtimestamp(int(unix_epoch)))
            convertedtime = utctime.astimezone(selectedtz)
            cur.execute('update systemconfig set timezone = ?', (arg,))
            con.commit()
            await ctx.send("Timezone set to {}\n".format(arg) + "Time now is {}\n".format(convertedtime.strftime(timef)) + "Today's date is {}".format(convertedtime.strftime(datef)))
        except pytz.exceptions.UnknownTimeZoneError:
            await ctx.send("Unknown timezone given\nSee https://www.iana.org/time-zones for an up-to-date list!")

    @commands.command(name="schedule_event")
    @commands.has_role(873031116179800065)
    async def schedule_event(self, ctx, *args):
        """
        Schedules an event
        """
        if not args:
            await ctx.send("Syntax: $schedule_event EventName DD/MM/YYYY HH:MM in 24hr format {}".format(ctx.message.author.mention))
        elif not args[1][2] == '/' and not args[1][5] == '/':
            await ctx.send("Date is incorrectly formatted! Format is **DD/MM/YYYY**! {}".format(ctx.message.author.mention))
        elif not args[2][2] == ':':
            await ctx.send("Time is incorrectly formatted! Format is **HH:MM** in 24hr format! {}".format(ctx.message.author.mention))
        else:
            strdate = args[1].replace('/', '')
            strtime = args[2].replace(':', '')
            if args[0].lower() == 'all':
                await ctx.send("Yikes... **ALL** is a reserved keyword, soz :sweat_smile:")
            else:
                try:
                    cur.execute('insert into sessions values (?, ?, ?, ?)',
                                (args[0], strdate, strtime, ctx.message.author.id))
                    await ctx.send("Scheduled {} on {} at {}".format(args[0], args[1], args[2]))
                except sqlite3.IntegrityError as ex:
                    await ctx.send("Event **{}** already exists!".format(args[0]))
                    if config['debug_mode'] == True:
                        await ctx.send("*DEBUG*: {}".format(ex))
            con.commit()
        # print(strdate[:2] + '/' + strdate[2:4] + '/' + strdate[4:8])

    @commands.command(name="event_search")
    async def event_search(self, ctx, *args):
        """
        Searches for scheduled events using the query parameters provided
        """
        if not args:
            await ctx.send("Syntax: $event_search EventName {}\nUse **ALL** to show all scheduled events\nUse this to search for events matching the name (full or partial)".format(ctx.message.author.mention))
            await ctx.send("You can use % to match zero or more characters, or _ to match single character\nE.g. %is% will match **wise** and **isle**. \_is\_ will match **rise** but not **crisis**.")
        else:
            arglower = args[0].lower()
            if arglower == 'all':
                counter = 1
                looprun = False
                for row in cur.execute("select * from sessions"):
                    looprun = True
                    strdate = row[1][:2] + '/' + \
                        row[1][2:4] + '/' + row[1][4:8]
                    strtime = row[2][:2] + ':' + row[2][2:4]
                    await ctx.send("{}. Event **{}** scheduled on **{}** at **{}** by **{}**".format(counter, row[0], strdate, strtime, ctx.guild.get_member(int(row[3])).display_name))
                    counter += 1
                if looprun is False:
                    await ctx.send("There are no scheduled events")
            else:
                counter = 1
                looprun = False
                for row in cur.execute("select * from sessions where session_name like ?", (args[0],)):
                    looprun = True
                    strdate = row[1][:2] + '/' + \
                        row[1][2:4] + '/' + row[1][4:8]
                    strtime = row[2][:2] + ':' + row[2][2:4]
                    await ctx.send("{}. Event **{}** scheduled on **{}** at **{}** by **{}**".format(counter, row[0], strdate, strtime,  ctx.guild.get_member(int(row[3])).display_name))
                    counter += 1
                if looprun is False:
                    await ctx.send("Your search returned no results")

    @commands.command(name="edit_event")
    @commands.has_role(873031116179800065)
    async def edit_event(self, ctx, *args):
        """
        Edits a scheduled event
        """
        if args:
            arglower = args[1].lower()
        if not args:
            await ctx.send("Syntax: $edit_event EventNameToEdit Name/Time/Date NewValue\nIf the name has a space be sure to use \"quotes\"\nE.g. $edit_event Event1 Time 15:00")
        elif arglower == 'name':
            try:
                cur.execute(
                    'update sessions set session_name = ? where session_name = ?', (args[2], args[0]))
                con.commit()
                await ctx.send("Event has been updated! Run **$event_search \"{}\"** to check".format(args[2]))
            except:
                await ctx.send("Something went wrong! Sorry :worried:")
        elif arglower == 'date':
            try:
                if not args[2][2] == '/' and not args[2][5] == '/':
                    await ctx.send("Date is incorrectly formatted! Format is **DD/MM/YYYY**! {}".format(ctx.message.author.mention))
                else:
                    strdate = args[2].replace('/', '')
                    cur.execute(
                        'update sessions set session_date = ? where session_name = ?', (strdate, args[0]))
                    con.commit()
                    await ctx.send("Event has been updated! Run **$event_search \"{}\"** to check".format(args[0]))
            except:
                await ctx.send("Something went wrong! Sorry :worried:")
        elif arglower == 'time':
            try:
                if not args[2][2] == ':':
                    await ctx.send("Time is incorrectly formatted! Format is **HH:MM** in 24hr format! {}".format(ctx.message.author.mention))
                else:
                    strtime = args[2].replace(':', '')
                    cur.execute(
                        'update sessions set session_time = ? where session_name = ?', (strtime, args[0]))
                    con.commit()
                    await ctx.send("Event has been updated! Run **$event_search \"{}\"** to check".format(args[0]))
            except:
                await ctx.send("Something went wrong! Sorry :worried:")

    @commands.command(name="remove_event")
    @commands.has_role(873031116179800065)
    async def remove_event(self, ctx, arg):
        """
        Removes any scheduled event
        """
        arglower = arg.lower()
        if arglower == 'all':
            cur.execute('delete from sessions')
            await ctx.send("All events have been removed")
        else:
            cur.execute('delete from sessions where session_name = ?', (arg,))
            await ctx.send("{} has been removed".format(arg))
        con.commit()


def setup(bot):
    bot.add_cog(scheduler(bot))
