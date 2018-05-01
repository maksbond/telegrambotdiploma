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

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from mwt import MWT
import logging
import constants as cons
from databases import InstructorDB
from utils import basicMethods
from utils import util

# Enable logging
logging.basicConfig(filename='/home/maksym_bondar/University/pybot/logs/pybot.log',
                    filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# GLOBAL VARIABLES
instructors = InstructorDB.InstructorDB()
select_course_first_step, select_course_second_step = range(2)


@MWT(timeout=60*60)
def get_admin_ids():
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return cons.admin_ids


def start(bot, update):
    instructor = instructors.find_instructor_by_id(update.message.from_user.id)
    reply_text = util.reply_text_unregistered_user()
    if instructor is not None:
        reply_text = basicMethods.reply_text_for_instrtructor(instructors, instructor)
    update.message.reply_text(reply_text)


def restart(bot, update):
    """restart bot"""
    if update.message.from_user.id in get_admin_ids():
        update.message.reply_text("Bot is restarted!")
        logging.info("Bot was restarted by {0} {1} with user id {2}".format(update.message.from_user.first_name,
                                                                            update.message.from_user.last_name,
                                                                            update.message.from_user.id))
    else:
        update.message.reply_text("You can't restart user. You have no permission!")
        logging.info("User with id {0} tried to restart bot".format(update.message.from_user.id))


# command for getting of help line
def help(bot, update):
    """Send a message when the command /help is issued."""
    helpListOfCommands = """
    Basic commands:\n/start - to start of conversation with bot\n/help - get list of available commands
    \nCommands for course(s):\n/select_course - select current course\n/get_info_about_course - get info about current course
    """
    update.message.reply_text(helpListOfCommands)


# command for getting of list with course(s)
def select_course(bot, update):
    instructor = instructors.find_instructor_by_id(update.message.from_user.id)
    if instructor is not None:
        buttons = instructors.return_courses_by_cursor(instructor)
        button_list = list()
        for button in buttons:
            button_list.append(InlineKeyboardButton(button, callback_data=button))
        reply_markup = InlineKeyboardMarkup(util.build_menu(button_list, n_cols=1))
        update.message.reply_text(
            u"Select the course you want to work with:",
            reply_markup=reply_markup
        )
        return select_course_first_step
    else:
        update.message.reply_text(util.reply_text_unregistered_user())


def first_select_course(bot, update):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton(u"Yes", callback_data=query.data)],
        [InlineKeyboardButton(u"No", callback_data="NO")]
    ]
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=u"Are you sure?"
    )
    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.edit_message_reply_markup(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=reply_markup
    )
    return select_course_second_step


def second_select_course(bot, update):
    query = update.callback_query
    if query.data is not "NO":
        instructors.update_current_course_by_id(query.message.chat_id, query.data)
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=u"You selected \"{}\" course!".format(query.data)
        )
    else:
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=u"You disable selecting of course!"
        )
    return


# handle request from chat
def button_handler(bot, update):
    query = update.callback_query
    bot.send_message(chat_id=query.message.chat_id, text="Selected option: {}".format(query.data))


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

    select_course_handler = ConversationHandler(
        entry_points=[CommandHandler("select_course", select_course)],
        states={
            select_course_first_step: [CallbackQueryHandler(first_select_course)],
            select_course_second_step: [CallbackQueryHandler(second_select_course)]
        },
        fallbacks=[CommandHandler("select_course", select_course)]
    )
    dp.add_handler(select_course_handler)

    dp.add_handler(CommandHandler("help", help))

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