import re
import os
import pickle
import hashlib
from openpyxl import Workbook, load_workbook
from colorama import Fore, Style, init
import logging
from datetime import datetime

init(autoreset=True)

logging.basicConfig(
    filename='student_system.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

STORAGE_FILE = "student_data.pkl"

class Student:
    def __init__(self, name, student_id, email, course_list, year_of_study, is_full_time):
        self.name = name
        self.student_id = student_id
        self.email = email
        self.course_list = course_list
        self.year_of_study = year_of_study
        self.is_full_time = is_full_time

    def add_course(self, course):
        if course not in self.course_list:
            self.course_list.append(course)
            logging.info(f"Course {course} added to student {self.student_id}.")
        else:
            print("Course already registered")

    def remove_course(self, course):
        if course in self.course_list:
            self.course_list.remove(course)
            logging.info(f"Course {course} removed from student {self.student_id}.")
        else:
            print("Course not found")

    def display_details(self):
        print(f"{Fore.CYAN}Name: {Fore.YELLOW}{self.name}")
        print(f"{Fore.CYAN}ID: {Fore.YELLOW}{self.student_id}")
        print(f"{Fore.CYAN}Email: {Fore.YELLOW}{self.email}")
        print(f"{Fore.CYAN}Courses: {Fore.YELLOW}{', '.join(self.course_list)}")
        print(f"{Fore.CYAN}Year of Study: {Fore.YELLOW}{self.year_of_study}")
        print(f"{Fore.CYAN}Full-time: {Fore.YELLOW}{'Yes' if self.is_full_time else 'No'}")
        print(Fore.MAGENTA + "-" * 40)

student_registration_list = {}

def save_data():
    with open(STORAGE_FILE, 'wb') as f:
        pickle.dump(student_registration_list, f)
    logging.info("Student data saved to persistent storage.")

def load_data():
    global student_registration_list
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'rb') as f:
            student_registration_list = pickle.load(f)
        logging.info("Student data loaded from persistent storage.")

def valid_email_format(email):
    return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)

def valid_course_code(course):
    return re.match(r"^[A-Z]{2,4}\d{3}$", course)

def display_all_students():
    if not student_registration_list:
        print("No students registered.")
    for student in student_registration_list.values():
        student.display_details()

def add_student():
    try:
        student_id = int(input("What is the student ID: "))
        if student_id in student_registration_list:
            print("Student ID already registered.")
            return

        name = input("What is the student name: ").strip()
        email = input("What is the student email: ").strip()
        if not valid_email_format(email):
            print("Invalid email format.")
            return

        course_list = input("Enter student course codes (e.g., CS123 IT345 ITX678): ").split()
        course_list = [course.strip().upper() for course in course_list]
        for course in course_list:
            if not valid_course_code(course):
                print(f"Invalid course code format: {course}")
                return

        year_of_study = int(input("What year of study is the student in (1-3): "))
        if year_of_study not in [1, 2, 3]:
            print("Enter a valid year of study (1, 2, or 3).")
            return

        full_time_status = input("Is the student full-time? (YES/NO): ").strip().upper()
        if full_time_status == "YES":
            full_time = True
        elif full_time_status == "NO":
            full_time = False
        else:
            print("Please enter YES or NO.")
            return

        student_registration_list[student_id] = Student(
            name, student_id, email, course_list, year_of_study, full_time
        )
        logging.info(f"Student {student_id} - {name} added.")
        save_data()
        print("Student successfully added.")

    except Exception as e:
        print("Error: Invalid format")
        print(str(e))

def enroll_course():
    try:
        stud_id = int(input("Enter student ID: "))
        if stud_id in student_registration_list:
            course = input("Enter course code to enroll: ").strip().upper()
            if not valid_course_code(course):
                print("Invalid course code format. Format must be like CS123.")
                return
            student_registration_list[stud_id].add_course(course)
            save_data()
        else:
            print("Student ID not found.")
    except ValueError:
        print("Invalid input. Student ID must be a number.")

def remove_student_course():
    try:
        stud_id = int(input("Enter student ID: "))
        if stud_id in student_registration_list:
            course = input("Enter course code to remove: ").strip().upper()
            if course in student_registration_list[stud_id].course_list:
                student_registration_list[stud_id].remove_course(course)
                save_data()
                print("Course successfully removed.")
            else:
                print("Course not found.")
        else:
            print("Student ID not found.")
    except ValueError:
        print("Invalid input. Student ID must be a number.")

def bubble_sort_year_of_study():
    sorted_list = list(student_registration_list.values())
    for i in range(len(sorted_list)):
        for j in range(0, len(sorted_list) - i - 1):
            if sorted_list[j].year_of_study > sorted_list[j + 1].year_of_study:
                sorted_list[j], sorted_list[j + 1] = sorted_list[j + 1], sorted_list[j]
    print("Students sorted by year of study (ascending):")
    for s in sorted_list:
        s.display_details()

def selection_sort_num_reg_course():
    sorted_list = list(student_registration_list.values())
    n = len(sorted_list)
    for i in range(n):
        max_index = i
        for j in range(i + 1, n):
            if len(sorted_list[j].course_list) > len(sorted_list[max_index].course_list):
                max_index = j
        sorted_list[i], sorted_list[max_index] = sorted_list[max_index], sorted_list[i]
    print("Students sorted by number of registered courses (descending):")
    for s in sorted_list:
        s.display_details()

def search_student():
    key = input("Enter student ID or Name to search: ").strip()
    logging.info(f"Search performed for student: {key}")
    found = False

    try:
        key_id = int(key)
        if key_id in student_registration_list:
            student_registration_list[key_id].display_details()
            return
    except ValueError:
        pass

    for student in student_registration_list.values():
        if student.name.lower() == key.lower():
            student.display_details()
            found = True

    if not found:
        print("Student not found.")

def export_to_excel():
    if not student_registration_list:
        print("No students to export.")
        return

    filename = input("Enter a name for the Excel file (without extension): ").strip()
    if not filename.lower().endswith(".xlsx"):
        filename += ".xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "Students"
    ws.append(["Student ID", "Name", "Email", "Courses", "Year of Study", "Full-time"])

    for student in student_registration_list.values():
        ws.append([
            student.student_id,
            student.name,
            student.email,
            ', '.join(student.course_list),
            student.year_of_study,
            "Yes" if student.is_full_time else "No"
        ])

    try:
        wb.save(filename)
        print(f"Student data successfully exported to '{filename}'")
    except Exception as e:
        print("Failed to save Excel file:", e)

def import_from_excel():
    filename = input("Enter the Excel filename to import (e.g., student_data.xlsx): ").strip()
    try:
        wb = load_workbook(filename)
        ws = wb.active

        for row in ws.iter_rows(min_row=2, values_only=True):
            student_id = int(row[0])
            name = row[1]
            email = row[2]
            course_list = [course.strip().upper() for course in row[3].split(',')] if row[3] else []
            year_of_study = int(row[4])
            is_full_time = True if row[5].strip().lower() == "yes" else False

            student_registration_list[student_id] = Student(
                name, student_id, email, course_list, year_of_study, is_full_time
            )

        save_data()
        print(f"Student data successfully imported from '{filename}'.")
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
    except Exception as e:
        print("Failed to import Excel file:", e)

def login():
    print("Login to the system")
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    users = {
        "admin": {"password": hashlib.sha256("admin123".encode()).hexdigest(), "role": "admin"},
        "student": {"password": hashlib.sha256("student123".encode()).hexdigest(), "role": "student"}
    }

    hashed_input = hashlib.sha256(password.encode()).hexdigest()
    if username in users and users[username]["password"] == hashed_input:
        logging.info(f"User '{username}' logged in successfully as {users[username]['role']}.")
        print(f"Welcome, {username} ({users[username]['role']})")
        return users[username]["role"]
    else:
        logging.warning(f"Failed login attempt with username '{username}'.")
        print("Invalid username or password.")
        return None

def user(role):
    while True:
        print("\nStudent Course Registration System")

        if role == "admin":
            print("1. Display All Students")
            print("2. Add New Student")
            print("3. Search Student by ID or Name")
            print("4. Enroll Student in a Course")
            print("5. Remove Student Course")
            print("6. Sort by Year of Study (Bubble Sort)")
            print("7. Sort by Number of Courses (Selection Sort)")
            print("8. Export Student Data to Excel")
            print("9. Import Student Data from Excel")
            print("10. Logout")
            print("11. Exit")
        elif role == "student":
            print("1. Display All Students")
            print("2. Search Student by ID or Name")
            print("3. Logout")
            print("4. Exit")

        choice = input("Enter your choice: ")

        if role == "admin":
            if choice == '1':
                display_all_students()
            elif choice == '2':
                add_student()
            elif choice == '3':
                search_student()
            elif choice == '4':
                enroll_course()
            elif choice == '5':
                remove_student_course()
            elif choice == '6':
                bubble_sort_year_of_study()
            elif choice == '7':
                selection_sort_num_reg_course()
            elif choice == '8':
                export_to_excel()
            elif choice == '9':
                import_from_excel()
            elif choice == '10':
                print("Logging out...")
                return
            elif choice == '11':
                print("Exiting program.")
                exit()
            else:
                print("Invalid choice.")

        elif role == "student":
            if choice == '1':
                display_all_students()
            elif choice == '2':
                search_student()
            elif choice == '3':
                print("Logging out...")
                return
            elif choice == '4':
                print("Exiting program.")
                exit()
            else:
                print("Invalid choice.")

if __name__ == "__main__":
    try:
        load_data()
        while True:
            role = login()
            if role:
                user(role)
            else:
                retry = input("Try logging in again? (yes/no): ").strip().lower()
                if retry != 'yes':
                    print("Goodbye!")
                    break
    except Exception as e:
        print("\nExiting Program due to unexpected error:", e)
