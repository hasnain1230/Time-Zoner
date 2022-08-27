# Time-Zoner
TimeZoner is a bot that parses all messages within a Discord server. If a server member mentions a certain
time, TimeZoner will parse that time and convert that time into different time zones previously selected 
by that guild. 

## Add TimeZoner To Your Server!
You can add TimeZoner to your server [here](https://discord.com/api/oauth2/authorize?client_id=1012187317286477854&permissions=274877975616&scope=bot)!

## Introduction
TimeZoner will parse all messages in a Discord server and if a time in format recognized by TimeZoner (see [Valid Time Formats](#valid-time-formats))
is sent, then TimeZoner will convert the aforementioned time into all other times set by that guild that the
guild owner set by using !timezone_set in any of their Discord text channels.

For example: If two friends, Alice and Bob, Alice from New York City and Bob from London are planning to
come online for a meeting on Discord, TimeZoner convert the time mentioned into all other possible times for
so that everyone is aware of the accurate time they need to meet based on their respective time zones. 

```
Alice: Bob, I'll see you at 4:30 online after I get off work?
TimeZoner: 
4:30 A.M. in America/New_York to Europe/London is: 9:30 A.M.
4:30 P.M. in America/New_York to Europe/London is: 21:30 P.M.
4:30 A.M. in Europe/London to America/New_York is: 23:30 A.M.
4:30 P.M. in Europe/London to America/New_York is: 11:30 P.M.
Bob: Got it. See you then. 
```

This allows for people from different time zones to use their own time zones when speaking (which reduces
confusion between all parties involved). Additionally, this reduces having to do calculations (and potentially
making an error with such calculations) when converting between different time zones with people they after
another party mentioned a time in their own respective time zone, not converting for others in the chat.

## How To Use
Please refer to `HELP.md` for this.

## How It Works
Based on certain String formats provided by Python 3's excellent `datetime` module, TimeZoner can parse each
Discord message and determine if a time was mentioned. If a time was mentioned, then using `datetime`, TimeZoner can
convert that time into all other selected time zones (account for every possible combination of time zones used) to provide
users with the time that best suits their needs. 

## Valid Time Formats
Time Zoner uses `datetime` to parse time strings. Time Zoner currently recognizes the following time formats and will
only convert times in these formats:
- 24-Hour Time: (e.g: 23:11)
  - Please Note: Hours greater than 12 will only be recognized as 24-hour format. Some parts of the world still
  use 12-hour time and this bot was built with this primary function in mind. Thus, times with an hour less than or equal to
  12 will always be treated as 12-hour time as opposed to 24. 
  - In the future, I may develop a setting per server that allows for a default of 24-hour time or 12-hour time if it is 
  requested. 
- 12-Hour Time: (e.g: 11:11)
- 12-Hour Time With AM/PM Descriptor: (e.g: 11:11 AM/PM or 11am)
  - Please Note: I did not allow for just numbers only. So, for example, "See you at 6!" will not work because
  then all numbers will be parsed and that can becoming annoying/spammy and Discord may also invalidate/revoke my API Key because
  too many requests all at once are being made.

## Credits:
This bot is fully developed and maintained by me: `hasnain1230`. You can find me on Discord here: `Lucidity#4586`