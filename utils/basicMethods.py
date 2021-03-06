
# reply to course
def reply_text_for_instrtructor(table_of_instructors, instructor, courses):
    name = table_of_instructors.return_name_by_cursor(instructor)

    courses_list = [courses[x] for x in table_of_instructors.return_courses_by_cursor(instructor)]
    position = table_of_instructors.return_position_by_cursor(instructor)
    courses_list = ',\n'.join(courses_list)[:-2]
    current_course = table_of_instructors.return_current_course_by_cursor(instructor)
    reply_text = """
        Hi, {0}.\nHow are you feeling today?\n\nYou are {1} at FIT.\n\nYou have access to:\n{2}.
        """.format(name, position, courses_list)

    if current_course is not None:
        current_course = courses[current_course]
        reply_text += "\nYour current course is {}.".format(current_course)
    else:
        reply_text += "\nYour current course is not selected."
    reply_text += "\n\nYou can select current course using /select_course command.\n"
    return reply_text
