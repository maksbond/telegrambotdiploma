from pymongo import MongoClient

class Student:
    # constructor of class
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client.get_database("pybot")
        self.list_of_students = self.db.get_collection("list_of_students")

    # update student id
    def update_student_id(self, student_id, telegram_id):
        result = self.list_of_students.find({"student_id": student_id.upper()})
        if result is not None:
            self.list_of_students.update({"student_id": student_id.upper()}, {'$set': {"id": telegram_id}})
            print("Student {} telegram_id is successfully updated ".format(student_id))
            return True
        else:
            print("Student is not registered at system")
            return False

    # get information about student
    def get_info_about_student(self, telegram_id):
        result = self.list_of_students.find_one({"id": telegram_id})
        if result is not None:
            reply_message = "Welcome, {0} from {1} group to our bot system! Please select current course with " \
                            "/select_course command.".format(result["name"], result["group"])
        else:
            reply_message = "You are not registered at system! Please, tap /register to add your account to system."
        return reply_message

    # get student by telegram id
    def find_student_by_id(self, telegram_id):
        return self.list_of_students.find_one({"id": telegram_id})

    # get current course of instructor
    def return_current_course_by_id(self, telegram_id):
        result = self.find_student_by_id(telegram_id)
        if result is not None:
            return result["current_course"]
        else:
            return result

    # get courses of instructor
    def return_courses_by_cursor(self, Cursor):
        return Cursor["courses"]

    # update current course by id
    def update_current_course_by_id(self, telegram_id, new_current_course):
        self.list_of_students.update({"id": telegram_id}, {'$set': {'current_course': new_current_course}})
