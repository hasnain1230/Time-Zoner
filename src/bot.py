import ast
import logging
import re
import sys

import discord
import csv

from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from secrets import discord_token
import datetime
import zoneinfo

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='!', help_command=None)

color = int("0000FF", 16)


def check_guild_configuration(guild_id):
    with open("guild_timezones.csv", "r") as csvfile:
        reader = csv.reader(csvfile)

        for row in reader:
            if int(row[0]) == guild_id:
                return True, ast.literal_eval(row[1])

        return [False, ]


def log_time_zones(ctx, time_zones):
    csv_data = list()
    try:
        with open('guild_timezones.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)

            guild_present = False

            for row in reader:
                if int(row[0]) == ctx.guild.id:
                    guild_present = True
                    for item in ast.literal_eval(row[1]):
                        if item in time_zones:
                            csvfile.close()
                            return False, item

                    tz_list = list(ast.literal_eval(row[1]))

                    for zone in time_zones:
                        tz_list.append(zone)

                    row[1] = str(tuple(tz_list))

                csv_data.append(row)

    except FileNotFoundError:
        pass

    if guild_present:
        with open('guild_timezones.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(csv_data)
    else:
        with open('guild_timezones.csv', 'a') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([ctx.guild.id, time_zones])

    csvfile.close()

    return [True, ]


def check_valid_time(time):
    valid_formats = ("%H:%M", "%I:%M", "%I:%M%p", "%I%p")

    for time_format in valid_formats:
        try:
            # timezone = zoneinfo.ZoneInfo("Europe/London")
            _time = datetime.datetime.strptime(time, time_format)

            return True, time_format
        except ValueError:
            continue

    return [False, ]


def check_am_pm(am_pm_str):
    if am_pm_str.lower() == "am" or am_pm_str.lower() == "a.m" or am_pm_str.lower() == "a.m.":
        return "AM"
    elif am_pm_str.lower() == "pm" or am_pm_str.lower() == "p.m" or am_pm_str.lower() == "p.m.":
        return "PM"
    else:
        return None


"""
Some time zones are calculated differently based on the date. For example, in some middle eastern countries, there may
be a +/- 30 minute difference if the time in question is before or after a certain year. To put any potential issues to rest,
we take the current time zone, get the current date. If time_str is the next day, we update the day. If it's the same day,
we let it be. We do this because suppose if country X announces that on Jan 1st, all clocks in their country will be pushed
by thirty minutes and someone says on December 31st says, "My flight arrives tomorrow at 2:30pm" and the current time in that
country is 3:30pm. If we assume the date December 31st and convert the time, the converted time tomorrow will be 2:00pm because the day 
is still December 31st. This makes all future conversions inaccurate too. We need to update the date to January 1st to get accurate conversions
to other time zones. We are assuming all dates referenced will be in the future. By keeping the date current for that time zone, 
we can accurately make conversions for that time zone and all other time zones. 

Tl;dr: By having accurate times per time zone, we can eliminate weird edge cases in case a certain country decides to change their times. 
"""


def convert_time(_time, zone, convert_zone, format_str):
    zone_time = datetime.datetime.now(tz=zoneinfo.ZoneInfo(zone)).replace(hour=_time.hour, minute=_time.minute)

    print(format_str)

    if zone_time > datetime.datetime.now(tz=zoneinfo.ZoneInfo(zone)):
        zone_time = zone_time.astimezone(zoneinfo.ZoneInfo(convert_zone))
        return zone_time.strftime(format_str)
    else:
        zone_time = zone_time.replace(day=_time.day + 1).astimezone(zoneinfo.ZoneInfo(convert_zone))
        return zone_time.strftime(format_str)


def return_conversions_embed(time_str, time_format, guild_timezones):
    _time = datetime.datetime.strptime(time_str, time_format)
    description = ""

    if time_format == "%-H:%M" and _time.hour > 12:
        for zone in guild_timezones:
            for convert_zone in guild_timezones:
                if zone == convert_zone:
                    continue
                else:
                    description += f":arrow_right: **{_time.strftime(time_format)}** in **{zone}** to **{convert_zone}** is: **{convert_time(_time, zone, convert_zone, time_format)}**\n"

    elif time_format == "%I:%M" or time_format == "%H:%M":
        time_format = "%-I:%M" if time_format == "%I:%M" else "%-H:%M"
        for zone in guild_timezones:
            for convert_zone in guild_timezones:
                if zone == convert_zone:
                    continue
                else:
                    _time = datetime.datetime.strptime(f"{time_str}am", "%I:%M%p")
                    description += f":arrow_right: **{_time.strftime('%-I:%M')} A.M.** in **{zone}** to **{convert_zone}** is: **{convert_time(_time, zone, convert_zone, time_format)}.**\n"
                    _time = datetime.datetime.strptime(f"{time_str}pm", "%I:%M%p")
                    description += f":arrow_right: **{_time.strftime('%-I:%M')} P.M.** in **{zone}** to **{convert_zone}** is: **{convert_time(_time, zone, convert_zone, time_format)}.**\n"

    elif time_format == "%I:%M%p" or time_format == "%I%p":
        time_format = "%-I:%M %p" if time_format == "%I:%M%p" else "%-I %p"

        for zone in guild_timezones:
            for convert_zone in guild_timezones:
                if zone == convert_zone:
                    continue
                else:
                    description += f":arrow_right: **{_time.strftime(time_format)} ** in **{zone}** to **{convert_zone}** is: **{convert_time(_time, zone, convert_zone, time_format)}.**\n"
    else:
        return None

    return description


@bot.event
async def on_ready():
    print(f"Logged in: {bot.user}")


@bot.add_listener
async def on_command_error(ctx, error):
    print(error, file=sys.stderr)

    if isinstance(error, MissingPermissions):
        embed = discord.Embed(title="Missing Permissions", description="You do not have permission for this command",
                              color=color)

        await ctx.channel.send(embed=embed)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    guild_timezones = check_guild_configuration(message.guild.id)

    if not guild_timezones[0]:  # If no time zone is set, then don't do anything. We do not want to spam the server.
        await bot.process_commands(message)
        return
    else:
        guild_timezones = guild_timezones[1]

    contents = message.content.split()
    _time = None

    for index in range(len(contents)):
        _time = None
        if contents[index][0].isnumeric():
            contents[index] = re.sub(r"[^\w:]", "", contents[index])
            try:
                am_pm = check_am_pm(contents[index + 1])
                if am_pm:
                    time = f"{contents[index]}{am_pm}"
                    _time = check_valid_time(time)
                else:
                    _time = check_valid_time(contents[index])
            except IndexError:
                _time = check_valid_time(contents[index])

            if _time[0]:
                description = return_conversions_embed(contents[index], _time[1], guild_timezones)
                if description is not None:
                    embed = discord.Embed(title="Time Conversions", description=description, color=color)

                    await message.channel.send(embed=embed)

    await bot.process_commands(message)


@bot.command(name="timezone_set", aliases=["tz_set"])
@has_permissions(administrator=True)
async def timezone_set(ctx, *timezone: str):
    invalid_zone = None

    try:
        for zone in timezone:
            invalid_zone = zone
            _timezone = zoneinfo.ZoneInfo(zone)

        duplicate = log_time_zones(ctx, timezone)

        if not duplicate[0]:
            description = f"The time zone **{duplicate[1]}** has already been saved for your server. Use `timezone_unset` or" \
                          f" `tz_unset` to unset this time zone. Additionally, you can use timezone unset all or " \
                          f"tz_unset_all to remove all currently active time zones"

            embed = discord.Embed(title="Time Zone Already Set", description=description, color=color)

            await ctx.channel.send(embed=embed)
            return
        else:
            embed = discord.Embed(title="Time Zone Successfully Set", description="Your configuration has been saved",
                                  color=color)

            await ctx.channel.send(embed=embed)
            return

    except zoneinfo.ZoneInfoNotFoundError:
        description = f"Sorry, **{invalid_zone}** is not a valid time zone. Please refer [here]" \
                      f"(https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for a list of valid time zone " \
                      f"paths."
        embed = discord.Embed(title="Invalid Timezone", description=description, color=color)

        await ctx.channel.send(embed=embed)
        return

    except ValueError:
        description = f"Sorry, **{invalid_zone}** is not a valid time zone. Please refer [here]" \
                      f"(https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for a list of valid time zone " \
                      f"paths."
        embed = discord.Embed(title="Invalid Timezone", description=description, color=color)

        await ctx.channel.send(embed=embed)
        return


@bot.command(name="get_all_timezones",
             aliases=["tz_get_all", "get_all_zones", "zones_get_all", "zonegetall", "tz_list_all"])
async def get_all_timezones(ctx):
    description = f"Please refer [here]" \
                  f"(https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for a list of valid time zone " \
                  f"paths."
    embed = discord.Embed(title="Time Zone List", description=description, color=color)
    await ctx.channel.send(embed=embed)


@bot.command(name="list_set_timezones", aliases=["tz_list_set"])
async def list_set_timezones(ctx):
    with open("guild_timezones.csv", 'r') as csvfile:
        reader = csv.reader(csvfile)

        for row in reader:
            if int(row[0]) == ctx.guild.id:
                description = "Here are a list of currently active time zones:\n"
                active_zones = ast.literal_eval(row[1])
                for timezone in active_zones:
                    description += f":arrow_right: {timezone}\n"

                embed = discord.Embed(title="Currently Active Timezones", description=description, color=color)

                await ctx.channel.send(embed=embed)
                return

        embed = discord.Embed(title="No Active Timezones Set",
                              description="There are currently no active time zones set for this server", color=color)
        await ctx.channel.send(embed=embed)


@bot.command(name="timezone_unset", aliases=["tz_unset"])
@has_permissions(administrator=True)
async def timezone_unset(ctx, *time_zones: str):
    for zones in time_zones:
        try:
            zoneinfo.ZoneInfo(zones)
        except zoneinfo.ZoneInfoNotFoundError:
            embed = discord.Embed(title="Time Zone Not Found", description=f"{zones} Not A Valid Timezone", color=color)
            await ctx.channel.send(embed=embed)

    modified_logs = list()

    with open("guild_timezones.csv", 'r') as csvfile:
        reader = csv.reader(csvfile)

        for row in reader:
            if int(row[0]) == ctx.guild.id:
                active_timezones = set(ast.literal_eval(row[1]))
                # row[1] = str(active_timezones - set(time_zones)) # Even though sets are much faster, I needed to check and return an error message in case the given time zone(s) were not in the current logs

                for zone in time_zones:
                    try:
                        active_timezones.remove(zone)
                    except KeyError:
                        embed = discord.Embed(title="Time Zone Unset Error",
                                              description="This time zone has not been set for this server",
                                              color=color)
                        await ctx.channel.send(embed=embed)
                        return

                row[1] = str(tuple(active_timezones))
                print(row)

            modified_logs.append(row)

    csvfile.close()

    with open("guild_timezones.csv", 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(modified_logs)

    csvfile.close()


@bot.command(name="timezone_unset_all", aliases=["tz_unset_all"])
@has_permissions(administrator=True)
async def timezone_unset_all(ctx):
    lines = list()
    with open('guild_timezones.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        guild_found = False

        for row in reader:
            if int(row[0]) == ctx.guild.id:
                guild_found = True
                continue
            lines.append(row)

        if not guild_found:
            embed = discord.Embed(title="Server Not Found Error",
                                  description="Your server does not have time zones set.", color=color)
            await ctx.channel.send(embed=embed)
            csvfile.close()
            return

    csvfile.close()

    with open('guild_timezones.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(lines)

    embed = discord.Embed(title="All Time Zones Unset", description="All time zones for your server have been unset",
                          color=color)

    csvfile.close()

    await ctx.channel.send(embed=embed)


@bot.command(name="help")
async def help(ctx):
    embed = discord.Embed(title="Help Is Here!", description="You can view all TimeZoner commands [here](https://github.com/hasnain1230/Time-Zoner/blob/main/HELP.md)", color=color)
    await ctx.author.send(embed=embed)

@bot.command(name="source")
async def source(ctx):
    embed = discord.Embed(title="But How It Work?", description="You can view TimeZoner's source code [here](https://github.com/hasnain1230/Time-Zoner)", color=color)
    await ctx.author.send(embed=embed)


if __name__ == '__main__':
    TOKEN = discord_token.TOKEN
    handler = logging.FileHandler(filename="/dev/stderr", encoding='utf-8', mode='w')
    bot.run(TOKEN, log_handler=None)
