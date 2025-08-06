# models.py
import logging
import heapq
import itertools
import json
from datetime import datetime, timezone
from colorama import Fore, Style, init

# counter for unique request IDs
_request_id_counter = itertools.count(1)


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

    def display_history(self):
        """
        Prints the student's course registration history in reverse chronological order.
        """
        node = self.history_head
        print(f"Course History for Student {self.student_id} ({self.name}):")
        if not node:
            print("  <no history>")
            return
        while node:
            ts = node.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            print(f"  {ts}: {node.action.upper()} {node.course_code}")
            node = node.next


class StudentRequest:
    def __init__(self, student_id, request_type, priority_level, request_details,
                 timestamp=None, request_id=None):
        self.request_id      = request_id or next(_request_id_counter)
        self.student_id      = student_id
        self.request_type    = request_type
        self.priority_level  = priority_level
        self.request_details = request_details
        self.timestamp       = timestamp or datetime.now(timezone.utc)

    def __repr__(self):
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return (f"<Req req_id={self.request_id} stud_id={self.student_id!r} "
                f"type={self.request_type!r} prio={self.priority_level} time={ts}>")

    def to_dict(self):
        return {
            "student_id":      self.student_id,
            "request_type":    self.request_type,
            "priority_level":  self.priority_level,
            "request_details": self.request_details,
            "timestamp":       self.timestamp.isoformat(),
            "request_id":      self.request_id
        }

    @classmethod
    def from_dict(cls, d):
        ts = datetime.fromisoformat(d["timestamp"])
        return cls(
            d["student_id"],
            d["request_type"],
            d["priority_level"],
            d["request_details"],
            timestamp=ts,
            request_id=d.get("request_id")
        )

    def __str__(self):
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return (f"[Req {self.request_id:>3}]  Student:{self.student_id:<6}  "
                f"Type:{self.request_type:<15}  Prio:{self.priority_level:<2}  Time:{ts}")


class RequestQueue:
    def __init__(self):
        self._heap    = []               # stores (priority, timestamp, counter, request)
        self._counter = itertools.count()  # FIFO tiebreaker

    def enqueue(self, req: StudentRequest):
        count = next(self._counter)
        heapq.heappush(self._heap, (req.priority_level, req.timestamp, count, req))

    def dequeue(self):
        if not self._heap:
            return None
        return heapq.heappop(self._heap)[3]

    def peek(self):
        if not self._heap:
            return None
        return self._heap[0][3]

    def is_empty(self):
        return not self._heap

    def size(self):
        return len(self._heap)

    def remove_request(self, request_id):
        self._heap = [
            (p, t, c, r)
            for (p, t, c, r) in self._heap
            if r.request_id != request_id
        ]
        heapq.heapify(self._heap)

    def remove_by_student_id(self, sid):
        self._heap = [
            (p, t, c, r)
            for (p, t, c, r) in self._heap
            if r.student_id != sid
        ]
        heapq.heapify(self._heap)

    def list_all(self):
        return [tup[3] for tup in sorted(self._heap)]

    def bulk_enqueue(self, requests):
        for req in requests:
            self.enqueue(req)

    def to_json(self):
        data = [r.to_dict() for r in self.list_all()]
        return json.dumps(data, indent=2)

    @classmethod
    def from_json(cls, json_str):
        q = cls()
        for item in json.loads(json_str):
            q.enqueue(StudentRequest.from_dict(item))
        return q

class TreeNode:
    def __init__(self, student: Student):
        self.student = student
        self.left = None    # smaller IDs
        self.right = None   # larger IDs

class StudentBST:
    def __init__(self):
        self.root = None

    def insert(self, student: Student):
        """Insert a Student into the BST."""
        if self.root is None:
            self.root = TreeNode(student)
        else:
            self._insert(self.root, student)

    def _insert(self, node: TreeNode, student: Student):
        if student.student_id < node.student.student_id:
            if node.left:
                self._insert(node.left, student)
            else:
                node.left = TreeNode(student)
        elif student.student_id > node.student.student_id:
            if node.right:
                self._insert(node.right, student)
            else:
                node.right = TreeNode(student)
        else:
            raise ValueError(f"Student ID {student.student_id} already exists")

    def search(self, student_id: int) -> Student | None:
        """Return the Student with that ID, or None if not found."""
        return self._search(self.root, student_id)

    def _search(self, node: TreeNode, student_id: int):
        if node is None:
            return None
        if student_id == node.student.student_id:
            return node.student
        elif student_id < node.student.student_id:
            return self._search(node.left, student_id)
        else:
            return self._search(node.right, student_id)

    def delete(self, student_id: int):
        """Remove a student by ID."""
        self.root = self._delete(self.root, student_id)

    def _delete(self, node: TreeNode, student_id: int):
        if node is None:
            return None
        if student_id < node.student.student_id:
            node.left = self._delete(node.left, student_id)
        elif student_id > node.student.student_id:
            node.right = self._delete(node.right, student_id)
        else:
            # -- node to delete found --
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            # two children: replace with inorder successor
            succ_parent, succ = node, node.right
            while succ.left:
                succ_parent, succ = succ, succ.left
            node.student = succ.student
            # unlink successor
            if succ_parent.left is succ:
                succ_parent.left = succ.right
            else:
                succ_parent.right = succ.right
        return node

    def in_order_traversal(self):
        """Yield all Students in-order (ascending ID)."""
        yield from self._in_order(self.root)

    def _in_order(self, node: TreeNode):
        if not node:
            return
        yield from self._in_order(node.left)
        yield node.student
        yield from self._in_order(node.right)

    def __contains__(self, student_id: int) -> bool:
        return self.search(student_id) is not None

    def __getitem__(self, student_id: int):
        student = self.search(student_id)
        if student is None:
            raise KeyError(f"{student_id!r} not found")
        return student

    def keys(self):
        return [s.student_id for s in self.in_order_traversal()]

    def values(self):
        return list(self.in_order_traversal())

    def items(self):
        return [(s.student_id, s) for s in self.in_order_traversal()]

    def __len__(self):
        return len(self.values())

    def __bool__(self):
        return bool(self.values())

    def print_tree(self, node=None, prefix="", is_left=True):
        """
        Recursively prints an ASCII view of the tree,
        showing each node’s student_id.
        """
        if node is None:
            node = self.root
            if node is None:
                print("<empty tree>")
                return

        # Print right subtree
        if node.right:
            self.print_tree(node.right,
                            prefix + ("│   " if is_left else "    "),
                            is_left=False)

        # Print this node
        connector = "└── " if is_left else "┌── "
        print(prefix + connector + str(node.student.student_id))

        # Print left subtree
        if node.left:
            self.print_tree(node.left,
                            prefix + ("    " if is_left else "│   "),
                            is_left=True)

class CourseHistoryNode:
    """
    A node in the linked list tracking a single course add/remove event.
    """
    def __init__(self, course_code: str, action: str, timestamp: datetime = None):
        self.course_code = course_code
        self.action = action  # 'add' or 'remove'
        self.timestamp = timestamp or datetime.now()
        self.next = None