# discord-radio
An internet radio bot for discord!

# discord-radio
### A Discord bot for streaming internet radio to a voice channel!

#### You will need to:
- Create an app in the Discord developer portal
- Generate a bot user
- Enable the correct intents
- Generate the invite URL
- Invite the bot to your server
- Define the required variables in config/config.py
- Execute the main.py script either directly or by creating a service wrapper

#### v2.0 ChangeLog 2023.03.20:
 - Variables in config/config.py are MANDATORY and this bot will not run without them!
 - Implemented slash commands!
   - /menu will generate an ephemeral message with a list of available stations
     - Note: This can be used for starting playback or changing the
             currently playing station if the bot is playing already.
   - /stop will stop playback and disconnect the bot from the voice channel
   - The bot will update its presence message with the currently playing station
