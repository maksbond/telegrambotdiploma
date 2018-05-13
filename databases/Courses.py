from pymongo import MongoClient
import datetime

class Course:
    # constructor of class
    def __init__(self, name_of_collection):
        client = MongoClient('localhost', 27017)

        db = client.get_database("pybot")
        self.collection_name = name_of_collection
        self.collection = db.get_collection(name_of_collection)

    def get_info_about_course(self):
        return self.collection.find_one({"info_about": {'$exists': True}})["info_about"]

    def get_name_of_course(self):
        course = self.collection.find_one({"info_about": {'$exists': True}})
        return course["course_name"]

    def insert_url_to_last_materials(self, type, text):
        element_to_insert = {
            "type": type,
            "text": text
        }
        self.collection.update_one({"last_materials": {'$exists': True}}, {'$push': {'last_materials': {'$each': [element_to_insert]}}})

    def insert_document_to_last_materials(self, type, file_id, file_name):
        element_to_insert = {
            "type": type,
            "file_id": file_id,
            "file_name": file_name
        }
        self.collection.update_one({"last_materials": {'$exists': True}}, {'$push': {'last_materials': {'$each': [element_to_insert]}}})

    def insert_other_elements_to_last_materials(self, type, file_id):
        element_to_insert = {
            "type": type,
            "file_id": file_id
        }
        self.collection.update_one({"last_materials": {'$exists': True}}, {'$push': {'last_materials': {'$each': [element_to_insert]}}})

    def get_list_of_last_materials(self):
        materials = self.collection.find_one({"last_materials": {'$exists': True}})
        return materials["last_materials"]

    def get_all_materials(self):
        materials = self.collection.find({"list_of_materials": {'$exists': True}})
        result = []
        for material in materials:
            result.append({"date": material["date"], "list_of_materials": material["list_of_materials"]})
        return result

    def update_last_materials(self):
        self.collection.update_one({"last_materials": {'$exists': True}},
                                   {'$set': {'last_materials': []}})

    def update_list_with_new_materials(self):
        materials = self.collection.find_one({"last_materials": {'$exists': True}})
        item_to_insert = {
            "date": datetime.datetime.now(),
            "list_of_materials": materials["last_materials"]
        }
        self.collection.insert_one(item_to_insert)

    def find_students_by_surname(self, name):
        return self.collection.find({"student_id": {'$exists': True}, "student_name": {'$regex': "^{}".format(name),
                                                                                       "$options": 'i'}})

    def insert_student_without_marks(self, student_id, student_name):
        self.collection.insert_one({"student_id": student_id, "student_name": student_name, "list_of_marks": [], "list_of_attendance": []})

    # update list of students
    def update_list_of_students(self, students_collection):
        students = students_collection.find({"courses": self.collection_name})
        list_of_students = []
        for student in students:
            item_to_insert = {
                "name": student["name"],
                "id": student["id"],
                "group": student["group"]
            }
            list_of_students.append(item_to_insert)
            current_student = self.collection.find_one({"student_id": student["id"]})
            if current_student is None:
                self.insert_student_without_marks(student["id"], student["name"])

        self.collection.update_one({"list_of_students": {'$exists': True}}, {'$set': {'list_of_students': list_of_students}})

    def set_mark_for_student(self, student_id, mark, date, type_of_work):
        student = self.collection.find_one({"student_id": student_id})
        element_to_insert = {
            "mark": mark,
            "date": date,
            "type_of_work": type_of_work
        }
        self.collection.update_one({"student_id": student["student_id"]}, {'$push': {'list_of_marks': {'$each': [element_to_insert]}}})

    def set_attendance_to_student(self, student_id, date):
        student = self.collection.find_one({"student_id": student_id})
        element_to_insert = {
            "date": date
        }
        self.collection.update_one({"student_id": student["student_id"]},
                                   {'$push': {'list_of_attendance': {'$each': [element_to_insert]}}})

    def get_attendance_of_student(self, student_id):
        student = self.collection.find_one({"student_id": student_id})
        return student["list_of_attendance"]

    def get_marks_of_student(self, student_id):
        student = self.collection.find_one({"student_id": student_id})
        return student["list_of_marks"]
