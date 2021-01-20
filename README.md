# AnonymousEirbot
## What the fuck is this ?
Well, it is based on a stupid idea.

On Telegram chats, admin users can enable an option to become invisible. When the option is enabled, the admin can write messages but the user name of the written messages will be the name of the chat. Thus, nobody really knows who has written the message.

From this feature, if everyone in the chat has the admin rights and has enabled the anonymous mode, everyone write messages with the user name of the chat name: in theory, it is impossible to know who writes what. The game is exactly to guess authors of the messages just with the content of the messages.

This bot allows to automatically promote incoming users in the chat to give admin rights to everybody, and to enable by default the anonymous mode for everyone.
This bot has also another feature to automatically delete messages in the chat after a configurable amount of time.
Obviously, the bot must have corresponding admin rights to perform these features.

## Usage
After adding the bot to a chat, an admin must give all the admin rights to the bot.

From this point, the bot will automatically give all admin rights to all the new incoming users in the chat. Users already in the chat before the arrival of the bot will not automatically gain admin rights. The command /admin can be used for these users to obtain admin rights. Replying to a message with the command /admin give admin rights to the user who wrote the replied message.

By default, all messages are deleted by the bot after 60 seconds. It can be configured with the /time command with a number of seconds in parameter. Example to set 1 hour:
/time 3600

The time value has no boundings, but timings will not be precise when setting a delete-time lower than 10s.

When the /time command is used, all the messages currently not deleted are affected by the new delete-time configured.

The messages written before the arrival of the bot are not automatically deleted.

The bot will always keep the last written message in the chat. Thus, the chat will never be totally empty.
## Cloning this code
To execute this code, you need to add a file "tokens" at the root of the repo. In this file, you need to put 2 tokens of 2 Telegram bots, on the first 2 lines. The first token is used in standard execution. The second token is used in test mode. On the third line of the file, you have to put your Telegram user ID (the number).

To run the bot, execute main.py in AnonymousEirbot/src/. Add the option -t to run the bot in test mode. Example:
py -3 main.py -t

In test mode, the bot runs with the second token, and is active only in the private chat between you and the bot (that is why you need to put your Telegram ID on the third line of the tokens file).

## How it works
The bot listens to all kind of messages in chats. When a new message is detected, the ID of the message and the date of the message are stored in a file in AnonymousEirbot/data/. The bot creates independant storage files for each chat.

In such a storage file, the first line is used to store the id of the user who added the bot in the chat, and the number of seconds before deleting each message. Each next lines are used to store message IDs and dates.

The bot has an alarm mechanism to delete messages. There is only one alarm mechanism for all the chats. The alarm is set to the next message to delete, from all participating chats. Thus, the bot can operate on different chats, with different delete time configurations.
