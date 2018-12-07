import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot, Chat
from telegram.error import (TelegramError, BadRequest ,TimedOut, ChatMigrated, NetworkError)
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get('TOKEN', None) # get token from command-line

# Welcomes the new member of the group
def welcomemessage(bot, update):
    print(update)
    msg = update.message
    # Google Sheets to get the previous Welcome message ID and update it with new message ID
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(r"pythonindiagooglesheets.json", scope)
    gc = gspread.authorize(credentials)
    wks = gc.open("Python India Welcome Message ID ").sheet1
    msg_id = int(wks.get_all_values()[0][0]) # Previous Welcome Message message ID

    try:
        bot.delete_message(chat_id=msg.chat_id, message_id=msg_id) # Deletes the previous Welcome message
    except BadRequest:
        print("Pervious message might be deleted")
    wks.update_cell(1, 1, msg.message_id + 1)
    bot.send_message(chat_id=msg.chat_id, text=f'Hey <a href="tg://user?id={msg.new_chat_members[0].id}">{msg.new_chat_members[0].first_name}</a>, Welcome to the Python India. We are grateful to have you as a part of us.', parse_mode='HTML')
    bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id) # Deletes the "'NAME' joined the group" Message

# Deletes a the left group message
def deleteleft(bot, update):
    msg = update.message
    bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

def main():
    updater = Updater(token=TOKEN)
    bot = updater.bot
    dispatcher = updater.dispatcher
    job = dispatcher.job_queue

    # Handlers Filters.status_update.new_chat_members
    welcomemessage_handler = MessageHandler(Filters.status_update.new_chat_members, welcomemessage)
    deleteleft_handler = MessageHandler(Filters.status_update.left_chat_member, deleteleft)

    # Dispatchers
    dispatcher.add_handler(welcomemessage_handler)
    dispatcher.add_handler(deleteleft_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
