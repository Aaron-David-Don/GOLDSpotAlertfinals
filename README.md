# GOLDSpotAlert
# This repo contains code that takes input from user and scrapes a gold rate website and notifies user through sms/whatsapp when the gold rate hits a user given value
# In order to make a telegram bot follow this step:
   -Open the telegram app and search for @BotFather.<br />
   -Click on the start button or send “/start”.<br />
   -Then send “/newbot” message to set up a name and a username.<br />
   -After setting name and username BotFather will give you an API token which is your bot token.\<br />
   -Then create an app on the telegram. <br />
   -Log into the telegram core: https://my.telegram.org<br />
   -Go to ‘API development tools’ and fill out the form.<br />
   -You will get the api_id and api_hash parameters required for user authorization. <br />
#
1. **GoldWatch.py**
   - This is the main code that takes the user input as different range for different products along with the mobile number and then with the help of playwright it will constantly check the website if the gold rate reaches the user value then it sends notification to the user through Telegram
