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

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity
from mwt import MWT
import logging
import constants as cons
from databases import *
import os
import re
import datetime

from utils import basicMethods
from utils import util

# Enable logging
logging.basicConfig(filename='/home/maksym_bondar/University/pybot/logs/pybot.log',
                    filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# GLOBAL VARIABLES
instructors = Instructor()
students = Student()
courses = []
courses_names = dict()
courses_info = dict()


@MWT(timeout=60*60)
def get_admin_ids():
    return cons.admin_ids


def get_course_by_id(name):
    for course in courses:
        if course.collection_name == name:
            return course



def update_students_list(bot, update):
    if update.message.from_user.id in get_admin_ids():
        for course in courses:
            course.update_list_of_students(students.list_of_students)
        update.message.reply_text("All lists is updated")
    else:
        update.message.reply_text("You do not have permission for this operation!")

def start_instructor(bot, update):
    instructor = instructors.find_instructor_by_id(update.message.from_user.id)
    reply_text = util.reply_text_unregistered_user()
    if instructor is not None:
        reply_text = basicMethods.reply_text_for_instrtructor(instructors, instructor, courses_names)
    update.message.reply_text(reply_text)


def start_student(bot, update):
    reply_text = students.get_info_about_student(update.message.from_user.id)
    update.message.reply_text(reply_text)


def get_info_about_course(bot, update):
    if bot.id == 580623948:
        current_course = instructors.return_current_course_by_id(update.message.from_user.id)
    elif bot.id == 573387240:
        current_course = students.return_current_course_by_id(update.message.from_user.id)
        if current_course is None:
            return
    reply_text = courses_info[current_course]
    update.message.reply_text(reply_text)


def register(bot, update):
    update.message.reply_text(u"Print you student id number in UA and uppercase")
    return cons.register_student_first_step


def register_student_first_step(bot, update):
    keyboard = [
        [InlineKeyboardButton(u"Yes", callback_data=update.message.text)],
        [InlineKeyboardButton(u"No", callback_data="NO")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(
        chat_id=update.message.chat_id,
        text=u"Are you sure?", reply_markup=reply_markup)
    return cons.register_student_second_step


def register_student_second_step(bot, update):
    query = update.callback_query
    if query.data != "NO":
        students.update_student_id(query.data, query.message.chat_id)
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=u"You updated your student ID! Print /start to check it!"
        )
    else:
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=u"You disable selecting of course!"
        )
        return cons.register_student_third_step
    return


def load_materials_for_course(bot, update):
    instructor = instructors.find_instructor_by_id(update.message.from_user.id)
    if instructor is not None:
        current_course = instructors.return_current_course_by_cursor(instructor)
        if current_course is not None:
            course = get_course_by_id(current_course)
            course.update_last_materials()
            current_course = courses_names[current_course]
            update.message.reply_text("Please, load files which you want to attach for {} course".format(current_course))
        else:
            update.message.reply_text("Please, /select_course to load some materials!")
    return cons.load_material_first_step


def first_load_material(bot, update):
    current_course = instructors.return_current_course_by_id(update.message.chat_id)
    course = get_course_by_id(current_course)

    if len(update.message.entities) > 0:
        type = 'url'
        text = update.message.text
        course.insert_url_to_last_materials(type, text)
    elif update.message.document is not None:
        type = "document"
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name
        _, document_extension = os.path.splitext(file_name)
        newFile = bot.get_file(file_id)
        newFile.download('documents/{0}{1}'.format(file_id, document_extension))
        course.insert_document_to_last_materials(type, file_id, file_name)
    elif len(update.message.photo) > 0:
        type = "photo"
        file_id = update.message.photo[-1].file_id
        newFile = bot.get_file(file_id)
        newFile.download('photos/{}.jpeg'.format(file_id))
        course.insert_other_elements_to_last_materials(type, file_id)
    elif update.message.video is not None:
        type = "video"
        file_id = update.message.video.file_id
        newFile = bot.get_file(file_id)
        newFile.download('videos/{}.mp4'.format(file_id))
        course.insert_other_elements_to_last_materials(type, file_id)
    elif update.message.audio is not None:
        type = "audio"
        file_id = update.message.audio.file_id
        newFile = bot.get_file(file_id)
        newFile.download('audios/{}.mp3'.format(file_id))
        course.insert_other_elements_to_last_materials(type, file_id)
    elif update.message.voice is not None:
        type = "voice"
        file_id = update.message.voice.file_id
        newFile = bot.get_file(file_id)
        newFile.download('voices/{}.ogg'.format(file_id))
        course.insert_other_elements_to_last_materials(type, file_id)

    keyboard = [
        [InlineKeyboardButton(u"Yes", callback_data="YES")],
        [InlineKeyboardButton(u"No", callback_data="NO")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(
        chat_id=update.message.chat_id,
        text=u"Want to send more files?",
        reply_markup=reply_markup
    )

    return cons.load_material_second_step


def second_load_material(bot, update):
    query = update.callback_query
    if query.data == "YES":
        instructor = instructors.find_instructor_by_id(query.message.chat_id)
        if instructor is not None:
            current_course = instructors.return_current_course_by_cursor(instructor)
            if current_course is not None:
                current_course = courses_names[current_course]
                bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text="Please, load files which you want to attach for {} course".format(current_course),
                )
        return cons.load_material_first_step
    else:
        keyboard = [
            [InlineKeyboardButton(u"Yes", callback_data="YES")],
            [InlineKeyboardButton(u"No", callback_data="NO")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=u"Want to add files to share list?",
        )
        bot.edit_message_reply_markup(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=reply_markup
        )
        return cons.load_material_third_step


def third_load_material(bot, update):
    query = update.callback_query
    instructor = instructors.find_instructor_by_id(query.message.chat_id)
    if instructor is not None:
        current_course = instructors.return_current_course_by_cursor(instructor)
        if current_course is not None:
            course = get_course_by_id(current_course)
    if query.data == "YES":
        bot.send_message(
            chat_id=query.message.chat_id,
            text=u"All materials successfully saved!")
    course.update_list_with_new_materials()
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=u"Loading of materials finished!",
    )
    return


def set_marks(bot, update):
    instructor = instructors.find_instructor_by_id(update.message.from_user.id)
    if instructor is not None:
        current_course = instructors.return_current_course_by_cursor(instructor)
        if current_course is not None:
            current_course = courses_names[current_course]
            update.message.reply_text(
                "Please, input first or more letter(s) of student surname which registered to '{}' course".format(current_course))
        else:
            update.message.reply_text("Please, /select_course to set marks!")
    return cons.set_marks_first_step


def first_set_marks(bot, update):
    current_course = instructors.return_current_course_by_id(update.message.from_user.id)
    student_surname = update.message.text[0].upper() + update.message.text[1:].lower()
    course = get_course_by_id(current_course)
    students_list = course.find_students_by_surname(student_surname)
    if students_list.count() != 0:
        keyboard = []
        for student in students_list:
            keyboard.append([InlineKeyboardButton(student["student_name"], callback_data=student["student_id"])])
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(
            chat_id=update.message.from_user.id,
            text=u"Choose student:",
            reply_markup=reply_markup)
        return cons.set_marks_second_step
    else:
        instructor = instructors.find_instructor_by_id(update.message.from_user.id)
        if instructor is not None:
            current_course = instructors.return_current_course_by_cursor(instructor)
            if current_course is not None:
                current_course = courses_names[current_course]
                bot.send_message(
                    chat_id=update.message.from_user.id,
                    text=u"There is no students with '{}' surname!".format(student_surname))
                bot.send_message(
                    chat_id=update.message.from_user.id,
                    text="Please, input first or more letter(s) of student surname which registered to '{}' course".format(
                        current_course))
        return cons.set_marks_first_step


def second_set_marks(bot, update):
    query = update.callback_query
    instructors.set_marks_to_student(int(query.data), query.message.chat_id)
    type_of_work = ""
    for key in cons.type_of_work.keys():
        type_of_work += key + " - " + cons.type_of_work[key] + ", "
    bot.send_message(
        chat_id=query.message.chat_id,
        text="Please, print mark in format: 'mark date(dd-mm-yyyy) type_of_work({})'".format(type_of_work[:-2]))
    return cons.set_marks_third_step


def third_set_marks(bot, update):
    result = update.message.text
    mark = [int(s) for s in result.split() if s.isdigit()][0]
    date = datetime.datetime.strptime(re.findall(r"\d\d-\d\d-\d\d\d\d", result)[0], '%d-%m-%Y')
    type_of_work = result[-1]
    instructor = instructors.find_instructor_by_id(update.message.from_user.id)
    if instructor is not None:
        current_course = instructors.return_current_course_by_cursor(instructor)
        if current_course is not None:
            course = get_course_by_id(current_course)
            student_id = instructors.get_marks_to_student(update.message.from_user.id)
            course.set_mark_for_student(student_id, mark, date, cons.type_of_work[type_of_work])
    student = students.find_student_by_id(student_id)
    bot.send_message(
        chat_id=update.message.from_user.id,
        text="You successfully set mark for {}".format(student["name"]))
    instructors.delete_set_marks_for_student(update.message.from_user.id)
    return


def set_attendance(bot, update):
    instructor = instructors.find_instructor_by_id(update.message.from_user.id)
    if instructor is not None:
        current_course = instructors.return_current_course_by_cursor(instructor)
        if current_course is not None:
            current_course = courses_names[current_course]
            update.message.reply_text(
                "Please, input first or more letter(s) of student surname which registered to '{}' course".format(current_course))
        else:
            update.message.reply_text("Please, /select_course to set attendance!")
    return cons.set_attendance_first_step


def first_set_attendance(bot, update):
    current_course = instructors.return_current_course_by_id(update.message.from_user.id)
    student_surname = update.message.text[0].upper() + update.message.text[1:].lower()
    course = get_course_by_id(current_course)
    students_list = course.find_students_by_surname(student_surname)
    if students_list.count() != 0:
        keyboard = []
        for student in students_list:
            keyboard.append([InlineKeyboardButton(student["student_name"], callback_data=student["student_id"])])
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(
            chat_id=update.message.from_user.id,
            text=u"Choose student:",
            reply_markup=reply_markup)
        return cons.set_attendance_second_step
    else:
        instructor = instructors.find_instructor_by_id(update.message.from_user.id)
        if instructor is not None:
            current_course = instructors.return_current_course_by_cursor(instructor)
            if current_course is not None:
                current_course = courses_names[current_course]
                bot.send_message(
                    chat_id=update.message.from_user.id,
                    text=u"There is no students with '{}' surname!".format(student_surname))
                bot.send_message(
                    chat_id=update.message.from_user.id,
                    text="Please, input first or more letter(s) of student surname which registered to '{}' course".format(
                        current_course))
        return cons.set_attendance_first_step


def second_set_attendance(bot, update):
    query = update.callback_query
    instructors.set_attendance_to_student(int(query.data), query.message.chat_id)
    bot.send_message(
        chat_id=query.message.chat_id,
        text="Please, print attendance in format: 'dd-mm-yyyy'")
    return cons.set_attendance_third_step


def third_set_attendance(bot, update):
    result = update.message.text
    date = datetime.datetime.strptime(re.findall(r"\d\d-\d\d-\d\d\d\d", result)[0], '%d-%m-%Y')
    instructor = instructors.find_instructor_by_id(update.message.from_user.id)
    if instructor is not None:
        current_course = instructors.return_current_course_by_cursor(instructor)
        if current_course is not None:
            course = get_course_by_id(current_course)
            student_id = instructors.get_attendance_to_student(update.message.from_user.id)
            course.set_attendance_to_student(student_id, date)
    student = students.find_student_by_id(student_id)
    bot.send_message(
        chat_id=update.message.from_user.id,
        text="You successfully set attendance for {}".format(student["name"]))
    instructors.delete_set_attendance_for_student(update.message.from_user.id)
    return


def get_all_materials(bot, update):
    current_course = students.return_current_course_by_id(update.message.from_user.id)
    if current_course is not None:
        course = get_course_by_id(current_course)
        list_of_materials = course.get_all_materials()
        call_back = ""
        if len(list_of_materials) > 0:
            call_back = "You got all materials!"
            for materials in list_of_materials:
                bot.send_message(
                    chat_id=update.message.from_user.id,
                    text=u"Here is loaded materials from {} to course:".format(materials["date"].strftime("%d-%b-%Y")))
                materials = materials["list_of_materials"]
                for material in materials:
                    material_type = material["type"]
                    if material_type == 'url':
                        bot.send_message(
                            chat_id=update.message.from_user.id,
                            text=material["text"])
                    elif material_type == "document":
                        _, document_extension = os.path.splitext(material["file_name"])
                        bot.send_document(
                            chat_id=update.message.from_user.id,
                            document=open('documents/{0}{1}'.format(material["file_id"], document_extension), 'rb'),
                            filename=material["file_name"])
                    elif material_type == "photo":
                        bot.send_photo(
                            chat_id=update.message.from_user.id,
                            photo=open('photos/{}.jpeg'.format(material["file_id"]), 'rb'))
                    elif material_type == "video":
                        bot.send_video(
                            chat_id=update.message.from_user.id,
                            video=open('videos/{}.mp4'.format(material["file_id"]), 'rb'))
                    elif material_type == "audio":
                        bot.send_audio(
                            chat_id=update.message.from_user.id,
                            audio=open('audios/{}.mp3'.format(material["file_id"]), 'rb'))
                    elif material_type == "voice":
                        bot.send_voice(
                            chat_id=update.message.from_user.id,
                            voice=open('voices/{}.ogg'.format(material["file_id"]), 'rb'))
        else:
            call_back = "Instructor did not load materials to current course"
    bot.send_message(
        chat_id=update.message.from_user.id,
        text=call_back)


def get_last_materials(bot, update):
    current_course = students.return_current_course_by_id(update.message.from_user.id)
    if current_course is not None:
        course = get_course_by_id(current_course)
        list_of_last_materials = course.get_list_of_last_materials()
        call_back = ""
        if len(list_of_last_materials) > 0:
            bot.send_message(
                chat_id=update.message.from_user.id,
                text=u"Here is last loaded materials from course:")
            call_back = "You get all materials!"
            for material in list_of_last_materials:
                material_type = material["type"]
                if material_type == 'url':
                    bot.send_message(
                        chat_id=update.message.from_user.id,
                        text=material["text"])
                elif material_type == "document":
                    _, document_extension = os.path.splitext(material["file_name"])
                    bot.send_document(
                        chat_id=update.message.from_user.id,
                        document=open('documents/{0}{1}'.format(material["file_id"], document_extension), 'rb'),
                        filename=material["file_name"])
                elif material_type == "photo":
                    bot.send_photo(
                        chat_id=update.message.from_user.id,
                        photo=open('photos/{}.jpeg'.format(material["file_id"]), 'rb'))
                elif material_type == "video":
                    bot.send_video(
                        chat_id=update.message.from_user.id,
                        video=open('videos/{}.mp4'.format(material["file_id"]), 'rb'))
                elif material_type == "audio":
                    bot.send_audio(
                        chat_id=update.message.from_user.id,
                        audio=open('audios/{}.mp3'.format(material["file_id"]), 'rb'))
                elif material_type == "voice":
                    bot.send_voice(
                        chat_id=update.message.from_user.id,
                        voice=open('voices/{}.ogg'.format(material["file_id"]), 'rb'))
        else:
            call_back = "Instructor did not load materials to current course"
    bot.send_message(
        chat_id=update.message.from_user.id,
        text=call_back)


def get_marks(bot, update):
    current_course = students.return_current_course_by_id(update.message.from_user.id)
    if current_course is not None:
        course = get_course_by_id(current_course)
        list_of_marks = course.get_marks_of_student(update.message.from_user.id)
        if len(list_of_marks) != 0:
            result = "Mark | Date | Type_of_work\n"
            for mark in list_of_marks:
                result += "{0} | {1} | {2}\n".format(mark["mark"], mark["date"].strftime("%d-%b-%Y"), mark["type_of_work"])
            result = result[:-1]
        else :
            result = "You do not have marks from this course!"

        update.message.reply_text(result)


def get_attendance(bot, update):
    current_course = students.return_current_course_by_id(update.message.from_user.id)
    if current_course is not None:
        course = get_course_by_id(current_course)
        list_of_attendance = course.get_attendance_of_student(update.message.from_user.id)
        if len(list_of_attendance) != 0:
            result = "Dates:\n"
            for mark in list_of_attendance:
                result += "{0}\n".format(mark["date"].strftime("%d-%b-%Y"))
            result = result[:-1]
        else:
            result = "You do not have marks with your attendance for this course!"

        update.message.reply_text(result)


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
    if bot.id == 580623948:
        user = instructors.find_instructor_by_id(update.message.from_user.id)
    elif bot.id == 573387240:
        user = students.find_student_by_id(update.message.from_user.id)
    if user is not None:
        if bot.id == 580623948:
            buttons = instructors.return_courses_by_cursor(user)
        elif bot.id == 573387240:
            buttons = students.return_courses_by_cursor(user)

        button_list = list()
        for button in buttons:
            name = courses_names[button]
            button_list.append(InlineKeyboardButton(name, callback_data=button))
        reply_markup = InlineKeyboardMarkup(util.build_menu(button_list, n_cols=1))
        update.message.reply_text(
            u"Select the course you want to work with:",
            reply_markup=reply_markup
        )
        return cons.select_course_first_step
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
    return cons.select_course_second_step


def second_select_course(bot, update):
    query = update.callback_query
    if query.data is not "NO":
        if bot.id == 580623948:
            instructors.update_current_course_by_id(query.message.chat_id, query.data)
        elif bot.id == 573387240:
            students.update_current_course_by_id(query.message.chat_id, query.data)
        course = get_course_by_id(query.data)
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=u"You selected \"{}\" course!".format(course.get_name_of_course())
        )
    else:
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=u"You disable selecting of course!"
        )
    return


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updaterInstructor = Updater(cons.INSTRUCTOR_BOT_TOKEN)
    updaterStudent = Updater(cons.STUDENT_BOT_TOKEN)

    # Get the dispatcher to register handlers
    dpInstructor = updaterInstructor.dispatcher
    dpStudent = updaterStudent.dispatcher

    dpStudent.add_handler(CommandHandler("start", start_student))

    register_student_handler = ConversationHandler(
        entry_points=[CommandHandler("register", register)],
        states={
            cons.register_student_first_step: [MessageHandler(Filters.text, register_student_first_step)],
            cons.register_student_second_step: [CallbackQueryHandler(register_student_second_step)],
            cons.register_student_third_step: [CallbackQueryHandler(start_student)]
        },
        fallbacks=[CommandHandler("register", register)]
    )
    select_course_handler = ConversationHandler(
        entry_points=[CommandHandler("select_course", select_course)],
        states={
            cons.select_course_first_step: [CallbackQueryHandler(first_select_course)],
            cons.select_course_second_step: [CallbackQueryHandler(second_select_course)]
        },
        fallbacks=[CommandHandler("select_course", select_course)]
    )
    dpStudent.add_handler(register_student_handler)
    dpStudent.add_handler(select_course_handler)
    dpStudent.add_handler(CommandHandler("get_info_about_course", get_info_about_course))
    dpStudent.add_handler(CommandHandler("get_last_materials", get_last_materials))
    dpStudent.add_handler(CommandHandler("get_all_materials", get_all_materials))
    dpStudent.add_handler(CommandHandler("get_marks_from_course", get_marks))
    dpStudent.add_handler(CommandHandler("get_attendance_from_course", get_attendance))
    dpStudent.add_handler(CommandHandler("update_students_list", update_students_list))

    # on different commands - answer in Telegram
    dpInstructor.add_handler(CommandHandler("start", start_instructor))
    dpInstructor.add_handler(select_course_handler)
    dpInstructor.add_handler(CommandHandler("get_info_about_course", get_info_about_course))
    load_materials_handler = ConversationHandler(
        entry_points=[CommandHandler("load_materials", load_materials_for_course)],
        states={
            cons.load_material_first_step: [MessageHandler((Filters.document
                                                            | Filters.audio
                                                            | Filters.photo
                                                            | Filters.video
                                                            | Filters.voice
                                                            | (Filters.text & (Filters.entity(MessageEntity.URL) | Filters.entity(MessageEntity.TEXT_LINK)))
                                                            ), first_load_material)],
            cons.load_material_second_step: [CallbackQueryHandler(second_load_material)],
            cons.load_material_third_step: [CallbackQueryHandler(third_load_material)]
        },
        fallbacks=[CommandHandler("load_materials", load_materials_for_course)]
    )
    dpInstructor.add_handler(load_materials_handler)
    set_marks_handles = ConversationHandler(
        entry_points=[CommandHandler("set_marks", set_marks)],
        states={
            cons.set_marks_first_step: [MessageHandler(Filters.text, first_set_marks)],
            cons.set_marks_second_step: [CallbackQueryHandler(second_set_marks)],
            cons.set_marks_third_step: [MessageHandler(Filters.text, third_set_marks)]
        },
        fallbacks=[CommandHandler("set_marks", set_marks)]
    )
    dpInstructor.add_handler(set_marks_handles)
    set_attendance_handles = ConversationHandler(
        entry_points=[CommandHandler("set_attendance", set_attendance)],
        states={
            cons.set_attendance_first_step: [MessageHandler(Filters.text, first_set_attendance)],
            cons.set_attendance_second_step: [CallbackQueryHandler(second_set_attendance)],
            cons.set_attendance_third_step: [MessageHandler(Filters.text, third_set_attendance)]
        },
        fallbacks=[CommandHandler("set_attendance", set_marks)]
    )
    dpInstructor.add_handler(set_attendance_handles)
    dpInstructor.add_handler(CommandHandler("update_students_list", update_students_list))

    dpInstructor.add_handler(CommandHandler("help", help))

    # log all errors
    dpInstructor.add_error_handler(error)
    dpStudent.add_error_handler(error)

    # Start the Bot
    updaterInstructor.start_polling()
    updaterStudent.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updaterInstructor.idle()
    updaterStudent.idle()


if __name__ == '__main__':
    for course in cons.courses:
        crs = Course(course)
        courses.append(crs)
        courses_names[course] = crs.get_name_of_course()
        courses_info[course] = crs.get_info_about_course()
    main()
