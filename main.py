#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple Bot to reply to Telegram messages.

This program is dedicated to the public domain under the CC0 license.

This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from mwt import MWT
import logging
import constants as cons

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


@MWT(timeout=60*60)
def get_admin_ids():
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return cons.admin_ids

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def restart(bot, update):
    """restart bot"""
    if update.message.from_user.id in get_admin_ids(bot, update.message.chat_id):
        update.message.reply_text("Restart типо")


def help(bot, update):
    """Send a message when the command /help is issued."""
    helpListOfCommands = """
    Basic commands:\n/start - to start of conversation with bot\n/help - get list of available commands
    \nRegistration commands:\n/registration - register at system of progress monitoring\n/check - check if you are registered
    """
    update.message.reply_text(helpListOfCommands)


# handle request from chat
def button(bot, update):
    query = update.callback_query
    bot.send_message(chat_id=query.message.chat_id, text="Selected option: {}".format(query.data))


def registration(bot, update):
    """Send a message is user is registered at system"""
    button_list = [[InlineKeyboardButton(cons.list_of_departments[key], callback_data="/department "+key)] for key in cons.list_of_departments]
    reply_markup = InlineKeyboardMarkup(button_list)
    bot.send_message(chat_id=update.message.from_user.id, text="Виберіть кафердру, на якій навчаєтесь", reply_markup=reply_markup)


def check(bot, update):
    """Check if user is registered at system"""
    if update.message.from_user.id in cons.test_base_of_users:
        update.message.reply_text("Checked! You are registered!")
    else:
        update.message.reply_text("Checked! You are not registered!")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(cons.BOT_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("registration", registration))
    dp.add_handler(CommandHandler("check", check))
    dp.add_handler(CommandHandler("restart", check))
    dp.add_handler(CallbackQueryHandler(button))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()