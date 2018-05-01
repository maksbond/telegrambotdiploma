from pymongo import MongoClient


class InstructorDB:
    # constructor of class
    def __init__(self):
        client = MongoClient('localhost', 27017 )
        db_names = client.database_names()
        if "instructors" in db_names:
            self.db = client.get_database("instructors")
            self.list_of_instructors = self.db.get_collection("list_of_instructors")

    # insert new instructor
    def insert_new_instructor(self, name, telegram_id, position, courses, current_course):
        item_to_insert = {
            "name": name,
            "id": telegram_id,
            "position": position,
            "courses": courses,
            "current_course": current_course
        }
        result = self.list_of_instructors.find({"id": telegram_id})
        if result.count() == 0:
            self.list_of_instructors.insert_one(item_to_insert)
            print("Instructor succesfully added to database")
        else:
            print("Instructor {} already exist".format(telegram_id))

    # get all instructors from database
    def get_all_instructors(self):
        return self.list_of_instructors.find()

    # find instructor by id
    def find_instructor_by_id(self, telegram_id):
        return self.list_of_instructors.find_one({"id": telegram_id})

    # get name of instructor
    def return_name_by_id(self, telegram_id):
        return self.find_instructor_by_id(telegram_id)["name"]

    # get position of instructor
    def return_position_by_id(self, telegram_id):
        return self.find_instructor_by_id(telegram_id)["position"]

    # get courses of instructor
    def return_courses_by_id(self, telegram_id):
        return self.find_instructor_by_id(telegram_id)["courses"]

    # get current course of instructor
    def return_current_course_by_id(self, telegram_id):
        return self.find_instructor_by_id(telegram_id)["current_course"]

    # get name of instructor
    def return_name_by_cursor(self, Cursor):
        return Cursor["name"]

    # get position of instructor
    def return_position_by_cursor(self, Cursor):
        return Cursor["position"]

    # get courses of instructor
    def return_courses_by_cursor(self, Cursor):
        return Cursor["courses"]

    # get current course of instructor
    def return_current_course_by_cursor(self, Cursor):
        return Cursor["current_course"]

    # update current course by id
    def update_current_course_by_id(self, telegram_id, new_current_course):
        self.list_of_instructors.update({"id": telegram_id}, {'$set': {'current_course': new_current_course}})
