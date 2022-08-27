# TimeZoner Commands And Configuration
> Bot Prefix: `!`
> <br><br>
> How To Read: <br>
> - Command arguments surrounded in {} mean that the command in question can also be invoked using descriptor given in {} <br>
> - Command arguments surrounded by () must be given when invoking a command.

## Commands
(These commands can be accessed by anyone regardless of their permissions)
- `!get_all_timezones`
  - Links user to a list of all valid time zones.
- `!list_set_timezones`
  - List the time zones currently set for the server, if any.
- `!help`
  - Provides a list of commands available to the server.
- `!source`
  - Provides a link to the source code of TimeZoner on GitHub.

## Administrator Commands
(Please Note: For the following commands, the user invoking these commands must be an administrator.)
- `!timezone_set {tz_set} (timezone(s) separated by spaces)`
  - With this command, you can set what time zones you want to active for your server. Based on these time zones you select,
  any time mentioned in any channel in your server will be converted all the time zones you set and select using this command.
- `!timezone_unset {tz_set} (timezone(s) separated by spaces)`
  - Will unset and de-activate the time zones you select. These time zones will no longer be converted in your server when
  a time is mentioned. 
- `!timezone_unset_all {tz_unset_all}`
  - Unsets and deactivates all active time zones in your server currently.
