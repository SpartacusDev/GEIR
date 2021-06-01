# GEIR
A Discord bot that searches for jailbreak packages in my [RestAPI](https://github.com/SpartacusDev/RestAPI) and announces when new iOS version get released or stop being signed!

## Commands
*help - A help command, what did you expect?

*invite - get an invite link to the bot

*info <device model> - Get the currently signed iOS versions for the device
  
*list - Get all compatible devices

*prefix <new prefix> - Sets a new prefix for the server
  
*setup <channel ID> - Sets an announcements channel for GEIR
  
*remove <channel ID> - Will stop announce in that said channel
  
*give_role <device model> - Adds/removes the device model role from the user

[[package]] - Gives you information about the first result with that name. Can be used everywhere in a sentence

*search <package> - Searches in our database for any packages with similar names

## Important Note!
GEIR creates roles for all compatible devices, and it will *not* remove them when you delete it. Even if you delete a role, it will recreate it after a day.

## Invite link
https://discord.com/api/oauth2/authorize?client_id=736195692858441758&permissions=8&scope=bot

## Contributing
Feel free to contribute by making a pull request

## Found an issue?
Please either file an issue here in the GitHub repo (I may not see it fast, which is why I suggest the second method more, which is:) or tell me the issue in the [Discord server](https://discord.gg/mZZhnRDGeg)