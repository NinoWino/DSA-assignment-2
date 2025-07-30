import re
import os
import pickle
import hashlib
from openpyxl import Workbook, load_workbook
from colorama import Fore, Style, init
import logging
from datetime import datetime, timedelta, timezone
import heapq
import itertools
import json
from collections import Counter
import random


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

def quick_sort_students(students):
    if len(students) <= 1:
        return students

    pivot = students[len(students) // 2]
    left, middle, right = [], [], []

    for s in students:
        # compare (year, name) tuples
        key = (s.year_of_study, s.name.lower())
        pivot_key = (pivot.year_of_study, pivot.name.lower())

        if key < pivot_key:
            left.append(s)
        elif key > pivot_key:
            right.append(s)
        else:
            middle.append(s)

    return quick_sort_students(left) + middle + quick_sort_students(right)


def quick_sort_year_name():
    students = list(student_registration_list.values())
    if not students:
        print("No students to sort.")
        return

    sorted_list = quick_sort_students(students)

    headers = ["ID", "Name", "Email", "Courses", "Year", "Full-time"]
    rows = [
        [
            str(s.student_id),
            s.name,
            s.email,
            ", ".join(s.course_list),
            str(s.year_of_study),
            "Yes" if s.is_full_time else "No"
        ]
        for s in sorted_list
    ]

    # compute column widths
    col_widths = [
        max(len(headers[i]), *(len(row[i]) for row in rows))
        for i in range(len(headers))
    ]

    # colourized header
    header_parts = [
        f"{Fore.CYAN}{Style.BRIGHT}{headers[i].ljust(col_widths[i])}{Style.RESET_ALL}"
        for i in range(len(headers))
    ]
    print(" | ".join(header_parts))
    print("-+-".join("-" * col_widths[i] for i in range(len(headers))))

    # colour rows by Year of Study: 1→red, 2→yellow, 3+→green
    for row in rows:
        yr = int(row[4])
        color = Fore.RED if yr == 1 else (Fore.YELLOW if yr == 2 else Fore.GREEN)
        line = " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers)))
        print(f"{color}{line}{Style.RESET_ALL}")


def merge_sort_students(students):
    """Recursively merge-sort by (num_courses, student_id)."""
    if len(students) <= 1:
        return students

    mid = len(students) // 2
    left = merge_sort_students(students[:mid])
    right = merge_sort_students(students[mid:])

    # merge step
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        left_key  = (len(left[i].course_list), left[i].student_id)
        right_key = (len(right[j].course_list), right[j].student_id)

        if left_key <= right_key:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    # append any leftovers
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def merge_sort_by_courses_and_id():
    students = list(student_registration_list.values())
    if not students:
        print("No students in the system.")
        return

    try:
        year = int(input("Enter Year of Study to display: ").strip())
    except ValueError:
        print("Invalid year. Please enter an integer.")
        return

    filtered = [s for s in students if s.year_of_study == year]
    if not filtered:
        print(f"No students found for Year {year}.")
        return

    sorted_list = merge_sort_students(filtered)

    headers = ["ID", "Name", "Email", "Courses", "Year", "Full-time"]
    rows = [
        [
            str(s.student_id),
            s.name,
            s.email,
            ", ".join(s.course_list),
            str(s.year_of_study),
            "Yes" if s.is_full_time else "No"
        ]
        for s in sorted_list
    ]

    # compute column widths
    col_widths = [
        max(len(headers[i]), *(len(row[i]) for row in rows))
        for i in range(len(headers))
    ]

    # colourized header
    header_parts = [
        f"{Fore.CYAN}{Style.BRIGHT}{headers[i].ljust(col_widths[i])}{Style.RESET_ALL}"
        for i in range(len(headers))
    ]
    print(" | ".join(header_parts))
    print("-+-".join("-" * col_widths[i] for i in range(len(headers))))

    # (all rows are same year, but we'll still colour by that year)
    for row in rows:
        yr = int(row[4])
        color = Fore.RED if yr == 1 else (Fore.YELLOW if yr == 2 else Fore.GREEN)
        line = " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers)))
        print(f"{color}{line}{Style.RESET_ALL}")

# in your module scope:
_request_id_counter = itertools.count(1)

class StudentRequest:
    def __init__(self, student_id, request_type, priority_level, request_details, timestamp=None, request_id=None):
        # assign a unique request_id if one wasn’t passed
        self.request_id = request_id or next(_request_id_counter)
        self.student_id = student_id
        self.request_type = request_type
        self.priority_level = priority_level
        self.request_details = request_details
        self.timestamp = timestamp or datetime.now(timezone.utc)

    def __repr__(self):
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return (f"<Req req_id={self.request_id} stud_id={self.student_id!r} "
                f"type={self.request_type!r} prio={self.priority_level} time={ts}>")


    def to_dict(self):
        """Serialize this request to a JSON‐friendly dict."""
        return {
            "student_id":      self.student_id,
            "request_type":    self.request_type,
            "priority_level":  self.priority_level,
            "request_details": self.request_details,
            # ISO format so it’s easy to parse back
            "timestamp":       self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, d):
        """Reconstruct a StudentRequest from a dict (e.g. loaded from JSON)."""
        ts = datetime.fromisoformat(d["timestamp"])
        return cls(d["student_id"], d["request_type"],
                   d["priority_level"], d["request_details"],
                   timestamp=ts)

    def __str__(self):
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"[Req {self.request_id:>3}]  "
            f"Student:{self.student_id:<6}  "
            f"Type:{self.request_type:<15}  "
            f"Prio:{self.priority_level:<2}  "
            f"Time:{ts}"
        )



class RequestQueue:
    def __init__(self):
        # the heap will store tuples: (priority_level, timestamp, counter, StudentRequest)
        self._heap    = []
        self._counter = itertools.count()

    def enqueue(self, req: StudentRequest):
        """Add a new StudentRequest to the queue."""
        count = next(self._counter)
        heapq.heappush(self._heap, (req.priority_level, req.timestamp, count, req))

    def bulk_enqueue(self, requests):
        """Enqueue a list (or any iterable) of StudentRequest objects."""
        for req in requests:
            self.enqueue(req)

    def dequeue(self):
        """Pop and return the highest-priority StudentRequest, or None if empty."""
        if not self._heap:
            return None
        _, _, _, req = heapq.heappop(self._heap)
        return req

    def peek(self):
        """Return the next StudentRequest without removing it."""
        if not self._heap:
            return None
        return self._heap[0][3]

    def is_empty(self):
        return not self._heap

    def size(self):
        return len(self._heap)

    def remove_by_student_id(self, sid):
        """
        Remove *all* requests matching the given student_id.
        Rebuilds the heap in O(n).
        """
        filtered = [(p, t, c, r) for (p, t, c, r) in self._heap if r.student_id != sid]
        self._heap = filtered
        heapq.heapify(self._heap)

    def list_all(self):
        """Return a sorted list of all pending requests (by priority then time)."""
        return [tup[3] for tup in sorted(self._heap)]

    def to_json(self):
        """
        Serialize the queue to a JSON string.
        You could also write this out to a file, or to a DB field.
        """
        # We sort so that JSON order matches processing order
        data = [req.to_dict() for req in self.list_all()]
        return json.dumps(data, indent=2)

    @classmethod
    def from_json(cls, json_str):
        """
        Reconstruct a RequestQueue from a JSON string as produced by to_json().
        """
        data = json.loads(json_str)
        q = cls()
        for item in data:
            req = StudentRequest.from_dict(item)
            q.enqueue(req)
        return q

# --- Example menu integration ---
request_queue = RequestQueue()

def process_request_menu():
    if request_queue.is_empty():
        print("No pending requests.")
        return
    req = request_queue.dequeue()
    print(f"Processing: {req}")
    # → here you’d put your real processing logic

def view_requests_menu():
    pending = request_queue.list_all()
    if not pending:
        print("No pending requests.")
    else:
        display_requests_table(pending)


def student_exists(sid):
    """
    Sequentially search through student_registration_list
    to see if a student with ID==sid is registered.
    """
    for key in student_registration_list.keys():
        if key == sid:
            return True
    return False

def add_request_menu():
    sid_input = input("Student ID: ").strip()
    try:
        sid = int(sid_input)
    except ValueError:
        print("Invalid Student ID format.")
        return

    # 3b. Validate student exists
    if not student_exists(sid):
        print(f"Student ID {sid} not found in system. Cannot add request.")
        return

    # 3b. Check for existing requests for this student (sequential search)
    existing = [r for r in request_queue.list_all() if r.student_id == sid]
    if existing:
        confirm = input(
            f"Student {sid} already has {len(existing)} pending request(s). "
            "Add another? (YES/NO): "
        ).strip().upper()
        if confirm != "YES":
            print("Request not added.")
            return

    # — then your original prompts:
    rtype = input("Request Type: ").strip()
    try:
        prio = int(input("Priority Level (integer, lower=more urgent): ").strip())
    except ValueError:
        print("Invalid priority; must be an integer.")
        return
    details = input("Request Details: ").strip()

    req = StudentRequest(sid, rtype, prio, details)
    request_queue.enqueue(req)
    print(f"Enqueued: {req}")

def view_queue_stats_menu():
    """
    3c. Show total, filter by type or priority, or give full breakdown.
    """
    total = request_queue.size()
    print(f"Total requests in queue: {total}\n")

    print("1. Filter by Request Type")
    print("2. Filter by Priority Level")
    print("3. Summary of all Request Types and Priority Levels")
    choice = input("Enter choice: ").strip()

    all_req = request_queue.list_all()
    if choice == '1':
        rt = input("Enter Request Type to filter: ").strip().lower()
        count = sum(1 for r in all_req if r.request_type.lower() == rt)
        print(f"{count} request(s) with type '{rt}'.")
    elif choice == '2':
        lvl_input = input("Enter Priority Level to filter: ").strip()
        try:
            lvl = int(lvl_input)
            count = sum(1 for r in all_req if r.priority_level == lvl)
            print(f"{count} request(s) with priority level {lvl}.")
        except ValueError:
            print("Invalid priority level.")
    elif choice == '3':
        types   = Counter(r.request_type for r in all_req)
        prios   = Counter(r.priority_level for r in all_req)
        print("Requests by Type:")
        for t, c in types.items():
            print(f"  {t}: {c}")
        print("\nRequests by Priority Level:")
        for p, c in sorted(prios.items()):
            print(f"  {p}: {c}")
    else:
        print("Invalid choice.")

def process_request_menu():
    """
    3d. Dequeue next request, show details, update count, log to file.
    """
    if request_queue.is_empty():
        print("No pending requests.")
        return

    req = request_queue.dequeue()
    print("Processing next request:\n")
    print(f"  Student ID     : {req.student_id}")
    print(f"  Request Type   : {req.request_type}")
    print(f"  Priority Level : {req.priority_level}")
    print(f"  Details        : {req.request_details}")
    print(f"  Timestamp      : {req.timestamp.isoformat()}\n")

    remaining = request_queue.size()
    print(f"Updated request count: {remaining}")

    # Log to processed_requests.log
    with open('processed_requests.log', 'a') as f:
        entry = {
            "processed_at": datetime.now(timezone.utc).isoformat(),
            **req.to_dict()
        }
        f.write(json.dumps(entry) + "\n")

    print("Request processed and logged.")

def display_requests_table(requests):
    headers = ["Req ID", "Student ID", "Type", "Priority", "Timestamp"]
    rows = [
        [
            r.request_id,
            r.student_id,
            r.request_type,
            r.priority_level,
            r.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        ]
        for r in requests
    ]
    col_widths = [
        max(len(str(val)) for val in [hdr] + [row[i] for row in rows])
        for i, hdr in enumerate(headers)
    ]

    # Colorized header
    header_parts = [
        f"{Fore.CYAN}{Style.BRIGHT}{headers[i].ljust(col_widths[i])}{Style.RESET_ALL}"
        for i in range(len(headers))
    ]
    print(" | ".join(header_parts))
    print("-+-".join("-" * col_widths[i] for i in range(len(headers))))

    # Colorized rows
    for row in rows:
        prio = row[3]
        color = Fore.RED if prio == 1 else (Fore.YELLOW if prio == 2 else Fore.GREEN)
        line = " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(headers)))
        print(f"{color}{line}{Style.RESET_ALL}")



def generate_dummy_requests(n):
    """
    Generate n dummy StudentRequest objects and enqueue them.
    Uses your existing request_queue.
    """
    sample_types = [
        "Password Reset", "Profile Update", "Transcript Request",
        "Course Enrollment", "Grade Appeal", "Fee Waiver"
    ]
    sample_details = {
        "Password Reset": "Forgot password, needs reset link.",
        "Profile Update": "Change of address and phone number.",
        "Transcript Request": "Official transcript for internship.",
        "Course Enrollment": "Add CS101 to my schedule.",
        "Grade Appeal": "Review grade for assignment 3.",
        "Fee Waiver": "Request waiver for late payment fee."
    }
    # if you want realistic student IDs, pick from your existing students:
    existing_ids = list(student_registration_list.keys())
    for _ in range(n):
        # pick a student ID (or make up a random one if list is empty)
        sid = random.choice(existing_ids) if existing_ids else random.randint(10000, 99999)

        # pick a request type
        rtype = random.choice(sample_types)

        # priority 1–5
        prio = random.randint(1, 5)

        # details based on type
        details = sample_details[rtype]

        # timestamp anywhere in the past week
        delta_secs = random.randint(0, 7 * 24 * 3600)
        ts = datetime.now(timezone.utc) - timedelta(seconds=delta_secs)

        req = StudentRequest(sid, rtype, prio, details, timestamp=ts)
        request_queue.enqueue(req)

    print(f"Enqueued {n} dummy requests.")

def dashboard_summary():
    """
    Dashboard Summary View:
      - Total number of students
      - Full-time vs Part-time counts
      - Most common course enrolled
      - Average courses per student
      - Total pending requests
      - Breakdown of requests by type
    """
    from collections import Counter

    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}📊 Dashboard Summary{Style.RESET_ALL}\n")

    # 1. Total / FT / PT students
    total_students = len(student_registration_list)
    full_time      = sum(1 for s in student_registration_list.values() if s.is_full_time)
    part_time      = total_students - full_time

    # 2. Most common course
    all_courses = [course for s in student_registration_list.values() for course in s.course_list]
    course_counts = Counter(all_courses)
    if course_counts:
        common_course, common_count = course_counts.most_common(1)[0]
    else:
        common_course, common_count = ("N/A", 0)

    # 3. Average courses per student
    avg_courses = (sum(len(s.course_list) for s in student_registration_list.values()) /
                   total_students) if total_students else 0.0

    # 4. Pending requests
    pending_requests = request_queue.size()

    # 5. Breakdown of requests by type
    req_types = Counter(r.request_type for r in request_queue.list_all())

    # — now print everything
    print(f"{Fore.CYAN}Total students:            {Fore.YELLOW}{total_students}")
    print(f"{Fore.CYAN} • Full-time:              {Fore.YELLOW}{full_time}")
    print(f"{Fore.CYAN} • Part-time:              {Fore.YELLOW}{part_time}\n")

    print(f"{Fore.CYAN}Most common course:        {Fore.YELLOW}{common_course} ({common_count})")
    print(f"{Fore.CYAN}Average courses/student:   {Fore.YELLOW}{avg_courses:.2f}\n")

    print(f"{Fore.CYAN}Pending student requests:  {Fore.YELLOW}{pending_requests}\n")

    print(f"{Fore.CYAN}Requests by Type:")
    if req_types:
        for typ, cnt in req_types.items():
            print(f"  {Fore.YELLOW}{typ:<20} {Fore.CYAN}→ {Fore.YELLOW}{cnt}")
    else:
        print(f"  {Fore.YELLOW}None")

    print()  # trailing blank line


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
            print(" 1. Display All Students")
            print(" 2. Add New Student")
            print(" 3. Search Student by ID or Name")
            print(" 4. Enroll Student in a Course")
            print(" 5. Remove Student Course")
            print(" 6. Sort by Year of Study (Bubble Sort)")
            print(" 7. Sort by Number of Courses (Selection Sort)")
            print(" 8. Sort by Num of Registered Course & Student ID (Merge Sort)")
            print(" 9. Sort by Year of Study (Quick Sort by Name)")
            print("10. Export to Excel")
            print("11. Import from Excel")
            print("12. Add Student Request to Queue")
            print("13. View Pending Student Requests")
            print("14. View Student Requests Queue Statistics")
            print("15. Process Next Student Request")
            print("16. Dashboard Summary")
            print("17. Logout")
            print("18. Exit")

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
                merge_sort_by_courses_and_id()
            elif choice == '9':
                quick_sort_year_name()
            elif choice == '10':
                export_to_excel()
            elif choice == '11':
                import_from_excel()
            elif choice == '12':
                add_request_menu()
            elif choice == '13':
                view_requests_menu()
            elif choice == '14':
                view_queue_stats_menu()
            elif choice == '15':
                process_request_menu()
            elif choice == '16':
                dashboard_summary()
            elif choice == '17':
                print("Logging out...")
                return
            elif choice == '18':
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
        generate_dummy_requests(50)
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
