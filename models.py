# models.py
import logging
import heapq
import itertools
import json
from datetime import datetime, timezone
import base64
from colorama import Fore, Style, init
import os
import cv2
import json
import numpy as np
from datetime import datetime

# counter for unique request IDs
_request_id_counter = itertools.count(1)

_ENCRYPTION_KEY = "mysecretkey"

def _xor_cipher(data: str) -> bytes:
    key = _ENCRYPTION_KEY
    return bytes([ord(data[i]) ^ ord(key[i % len(key)]) for i in range(len(data))])

def encrypt_field(plaintext: str) -> str:
    """Encrypts plaintext string to base64-encoded ciphertext."""
    cipher_bytes = _xor_cipher(plaintext)
    return base64.b64encode(cipher_bytes).decode('utf-8')

def decrypt_field(ciphertext: str) -> str:
    """Decrypts base64-encoded ciphertext back to plaintext."""
    cipher_bytes = base64.b64decode(ciphertext.encode('utf-8'))
    plain_chars = [chr(cipher_bytes[i] ^ ord(_ENCRYPTION_KEY[i % len(_ENCRYPTION_KEY)])) for i in range(len(cipher_bytes))]
    return ''.join(plain_chars)

class CourseHistoryNode:
    def __init__(self, course_code: str, action: str, timestamp: datetime = None):
        self.course_code = course_code
        self.action = action  # 'add' or 'remove'
        self.timestamp = timestamp or datetime.now()
        self.next = None

class Student:
    def __init__(self, name, student_id, email, course_list, year_of_study, is_full_time):
        self.name = name
        self.student_id = student_id
        # store encrypted email
        self._encrypted_email = encrypt_field(email)
        self.course_list = course_list
        self.year_of_study = year_of_study
        self.is_full_time = is_full_time
        # head of the linked list of history events
        self.history_head: CourseHistoryNode | None = None

    def __setstate__(self, state):
        # support unpickling older Student instances without history_head or encrypted_email
        self.__dict__.update(state)
        # migrate plaintext email if needed
        if hasattr(self, 'email') and not hasattr(self, '_encrypted_email'):
            self._encrypted_email = encrypt_field(self.email)
        if not hasattr(self, 'history_head'):
            self.history_head = None

    @property
    def email(self) -> str:
        """Decrypt and return the student's email."""
        try:
            return decrypt_field(self._encrypted_email)
        except Exception:
            return "<decrypt_error>"

    @email.setter
    def email(self, value: str):
        """Encrypt and store the student's email."""
        self._encrypted_email = encrypt_field(value)

    def add_course(self, course):
        if course not in self.course_list:
            self.course_list.append(course)
            logging.info(f"Course {course} added to student {self.student_id}.")
            # record history event
            node = CourseHistoryNode(course, 'add')
            node.next = self.history_head
            self.history_head = node
        else:
            print("Course already registered")

    def remove_course(self, course):
        if course in self.course_list:
            self.course_list.remove(course)
            logging.info(f"Course {course} removed from student {self.student_id}.")
            # record history event
            node = CourseHistoryNode(course, 'remove')
            node.next = self.history_head
            self.history_head = node
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

class FaceAuth:
    """
    Face enrollment and verification using OpenCV LBPHFaceRecognizer.
    Stores cropped face images per user.
    Requires: pip install opencv-contrib-python
    """
    def __init__(self, face_dir="faces", model_path="face_lbph_model.yml"):
        self.face_dir = face_dir
        self.model_path = model_path
        os.makedirs(self.face_dir, exist_ok=True)
        self.detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()

    def enroll(self, username: str, image_path: str):
        """Enroll a face image for a username."""
        img = cv2.imread(image_path)
        if img is None:
            raise RuntimeError("Image not found or cannot be read.")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        if len(faces) == 0:
            raise RuntimeError("No face detected in the image.")

        user_dir = os.path.join(self.face_dir, username)
        os.makedirs(user_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        for (x, y, w, h) in faces:
            face_crop = gray[y:y+h, x:x+w]
            face_crop = cv2.resize(face_crop, (200, 200))
            cv2.imwrite(os.path.join(user_dir, f"{ts}.png"), face_crop)
        print(f"✅ Face enrolled for '{username}'.")

    def train_model(self):
        """Train LBPH model on all enrolled faces."""
        faces, labels = [], []
        label_map = {}
        current_label = 0

        for username in os.listdir(self.face_dir):
            user_dir = os.path.join(self.face_dir, username)
            if not os.path.isdir(user_dir):
                continue
            label_map[current_label] = username
            for img_file in os.listdir(user_dir):
                path = os.path.join(user_dir, img_file)
                img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                faces.append(img)
                labels.append(current_label)
            current_label += 1

        if not faces:
            raise RuntimeError("No faces found for training.")

        self.recognizer.train(faces, np.array(labels))
        self.recognizer.write(self.model_path)

        # Save label map
        with open(self.model_path + ".labels.json", "w") as f:
            json.dump(label_map, f)
        print("✅ Model trained and saved.")

    def verify(self, image_path: str, threshold: float = 65.0):
        """Verify an image against trained model."""
        if not os.path.exists(self.model_path):
            raise RuntimeError("Model not trained yet. Call train_model() first.")

        # Load model + labels
        self.recognizer.read(self.model_path)
        with open(self.model_path + ".labels.json", "r") as f:
            label_map = json.load(f)

        img = cv2.imread(image_path)
        if img is None:
            raise RuntimeError("Image not found or cannot be read.")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        if len(faces) == 0:
            return False, "No face detected."

        for (x, y, w, h) in faces:
            face_crop = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
            label_id, confidence = self.recognizer.predict(face_crop)
            username = label_map[str(label_id)] if isinstance(label_map, dict) else label_map[label_id]
            if confidence <= threshold:
                return True, f"Match: {username} (confidence={confidence:.1f})"
            else:
                return False, f"Face mismatch (confidence={confidence:.1f})"

        return False, "No match found."
