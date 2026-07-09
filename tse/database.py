import pymysql
import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from tse.config import get_settings
from tse.utils.logger import logger

DATA_DIR = Path.home() / ".tse"
SQLITE_PATH = DATA_DIR / "tse.db"

class DatabaseManager:
    def __init__(self):
        self.settings = get_settings()
        self.is_sqlite = False
        self._conn = None
        self.init_db()

    def get_connection(self):
        """Attempts to connect to MySQL; falls back to SQLite if it fails."""
        if self.is_sqlite:
            conn = sqlite3.connect(SQLITE_PATH)
            # Enable dictionary-like rows for SQLite
            conn.row_factory = sqlite3.Row
            return conn, True

        try:
            conn = pymysql.connect(
                host=self.settings.db_host,
                port=self.settings.db_port,
                user=self.settings.db_user,
                password=self.settings.db_password,
                database=self.settings.db_name,
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=3
            )
            return conn, False
        except Exception as e:
            logger.warning(f"Failed to connect to MySQL database: {e}. Falling back to SQLite.")
            self.is_sqlite = True
            conn = sqlite3.connect(SQLITE_PATH)
            conn.row_factory = sqlite3.Row
            return conn, True

    def init_db(self):
        """Initializes the database schema."""
        # Create MySQL database if missing
        if not self.is_sqlite:
            try:
                conn = pymysql.connect(
                    host=self.settings.db_host,
                    port=self.settings.db_port,
                    user=self.settings.db_user,
                    password=self.settings.db_password,
                    connect_timeout=3
                )
                with conn.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.settings.db_name}")
                conn.close()
            except Exception as e:
                logger.warning(f"Could not create MySQL database '{self.settings.db_name}': {e}. Switching to SQLite.")
                self.is_sqlite = True

        conn, is_sqlite = self.get_connection()
        cursor = conn.cursor()

        # Schema templates
        if is_sqlite:
            auto_inc = "INTEGER PRIMARY KEY AUTOINCREMENT"
            text_type = "TEXT"
        else:
            auto_inc = "INT AUTO_INCREMENT PRIMARY KEY"
            text_type = "TEXT"

        # 1. Subjects table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS subjects (
                id {auto_inc},
                name VARCHAR(100) UNIQUE NOT NULL,
                description {text_type}
            )
        """)

        # 2. History table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS history (
                id {auto_inc},
                question {text_type} NOT NULL,
                answer {text_type} NOT NULL,
                timestamp DATETIME NOT NULL,
                favorite INT DEFAULT 0,
                tags VARCHAR(255),
                subject_id INT,
                exam_mode VARCHAR(50),
                marks INT,
                FOREIGN KEY(subject_id) REFERENCES subjects(id)
            )
        """)

        # 3. Flashcards table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS flashcards (
                id {auto_inc},
                question {text_type} NOT NULL,
                answer {text_type} NOT NULL,
                subject_id INT,
                box INT DEFAULT 1,
                next_review DATETIME,
                FOREIGN KEY(subject_id) REFERENCES subjects(id)
            )
        """)

        # 4. Quizzes table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS quizzes (
                id {auto_inc},
                question {text_type} NOT NULL,
                option_a VARCHAR(255) NOT NULL,
                option_b VARCHAR(255) NOT NULL,
                option_c VARCHAR(255) NOT NULL,
                option_d VARCHAR(255) NOT NULL,
                correct_option VARCHAR(10) NOT NULL,
                explanation {text_type},
                subject_id INT,
                FOREIGN KEY(subject_id) REFERENCES subjects(id)
            )
        """)

        # 5. Leaderboard table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS leaderboard (
                id {auto_inc},
                user_name VARCHAR(100) NOT NULL,
                score INT NOT NULL,
                subject_id INT,
                timestamp DATETIME NOT NULL,
                FOREIGN KEY(subject_id) REFERENCES subjects(id)
            )
        """)

        # 6. Document chunks table (For PDF Semantic search fallback)
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id {auto_inc},
                doc_name VARCHAR(255) NOT NULL,
                chunk_index INT NOT NULL,
                chunk_text {text_type} NOT NULL
            )
        """)

        conn.commit()

        # Prepopulate subjects
        subjects = [
            ("DBMS", "Database Management Systems"),
            ("MongoDB", "NoSQL Document Database Management"),
            ("Operating Systems", "OS Core Concepts (Process, Threads, Memory, I/O)"),
            ("Computer Networks", "OSI Model, TCP/IP, Routing Protocols, Socket Programming"),
            ("DAA", "Design and Analysis of Algorithms"),
            ("AI", "Artificial Intelligence & Logic"),
            ("ML", "Machine Learning Techniques & Models"),
            ("Biology", "Engineering Biology & Cellular Systems"),
            ("OR", "Operations Research & Linear Programming"),
            ("Engineering Mathematics", "Linear Algebra, Calculus, Prob & Stats, Numerical Methods")
        ]

        for sub, desc in subjects:
            try:
                if is_sqlite:
                    cursor.execute("INSERT OR IGNORE INTO subjects (name, description) VALUES (?, ?)", (sub, desc))
                else:
                    cursor.execute("INSERT IGNORE INTO subjects (name, description) VALUES (%s, %s)", (sub, desc))
            except Exception as e:
                logger.error(f"Error populating subject {sub}: {e}")

        conn.commit()
        conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Executes a query and returns a list of dictionaries."""
        conn, is_sqlite = self.get_connection()
        if is_sqlite:
            query = query.replace("%s", "?")
        
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            if query.strip().upper().startswith(("SELECT", "SHOW", "DESCRIBE")):
                rows = cursor.fetchall()
                # For SQLite, rows are sqlite3.Row objects, which we convert to dict
                # For PyMySQL, they are already dicts
                if is_sqlite:
                    return [dict(row) for row in rows]
                return list(rows)
            else:
                conn.commit()
                return []
        except Exception as e:
            logger.error(f"Database Query Error: {e} | Query: {query}")
            raise e
        finally:
            conn.close()

    def execute_write(self, query: str, params: tuple = ()) -> int:
        """Executes a write query and returns the last inserted row ID."""
        conn, is_sqlite = self.get_connection()
        if is_sqlite:
            query = query.replace("%s", "?")
            
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            if is_sqlite:
                return cursor.lastrowid
            else:
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Database Write Error: {e} | Query: {query}")
            conn.rollback()
            raise e
        finally:
            conn.close()

    # Subjects helpers
    def get_subjects(self) -> List[Dict[str, Any]]:
        return self.execute_query("SELECT id, name, description FROM subjects")

    def get_subject_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        res = self.execute_query("SELECT id, name, description FROM subjects WHERE name = %s", (name,))
        return res[0] if res else None

    # History helpers
    def add_history(self, question: str, answer: str, subject_id: Optional[int], exam_mode: str, marks: int, tags: str = "") -> int:
        query = """
            INSERT INTO history (question, answer, timestamp, favorite, tags, subject_id, exam_mode, marks)
            VALUES (%s, %s, %s, 0, %s, %s, %s, %s)
        """
        params = (question, answer, datetime.now(), tags, subject_id, exam_mode, marks)
        return self.execute_write(query, params)

    def get_history(self, subject_id: Optional[int] = None, search_term: str = "", favorite_only: bool = False) -> List[Dict[str, Any]]:
        query = """
            SELECT h.id, h.question, h.answer, h.timestamp, h.favorite, h.tags, h.exam_mode, h.marks, s.name as subject_name
            FROM history h
            LEFT JOIN subjects s ON h.subject_id = s.id
            WHERE 1=1
        """
        params = []
        if subject_id:
            query += " AND h.subject_id = %s"
            params.append(subject_id)
        if favorite_only:
            query += " AND h.favorite = 1"
        if search_term:
            query += " AND (h.question LIKE %s OR h.answer LIKE %s OR h.tags LIKE %s)"
            search_param = f"%{search_term}%"
            params.extend([search_param, search_param, search_param])
        
        query += " ORDER BY h.timestamp DESC"
        return self.execute_query(query, tuple(params))

    def toggle_favorite(self, history_id: int) -> bool:
        """Toggles the favorite state of a history item. Returns the new state."""
        item = self.execute_query("SELECT favorite FROM history WHERE id = %s", (history_id,))
        if not item:
            raise ValueError("History item not found")
        new_val = 1 if item[0]["favorite"] == 0 else 0
        self.execute_write("UPDATE history SET favorite = %s WHERE id = %s", (new_val, history_id))
        return bool(new_val)

    # Bookmarks helpers (bookmarks are just favorites in history)
    def get_bookmarks(self) -> List[Dict[str, Any]]:
        return self.get_history(favorite_only=True)

    # Flashcard helpers
    def add_flashcard(self, question: str, answer: str, subject_id: Optional[int]) -> int:
        query = """
            INSERT INTO flashcards (question, answer, subject_id, box, next_review)
            VALUES (%s, %s, %s, 1, %s)
        """
        params = (question, answer, subject_id, datetime.now())
        return self.execute_write(query, params)

    def get_due_flashcards(self, subject_id: Optional[int] = None) -> List[Dict[str, Any]]:
        query = """
            SELECT f.id, f.question, f.answer, f.box, f.next_review, s.name as subject_name
            FROM flashcards f
            LEFT JOIN subjects s ON f.subject_id = s.id
            WHERE f.next_review <= %s
        """
        params = [datetime.now()]
        if subject_id:
            query += " AND f.subject_id = %s"
            params.append(subject_id)
        return self.execute_query(query, tuple(params))

    def update_flashcard_leitner(self, card_id: int, correct: bool) -> None:
        card = self.execute_query("SELECT box FROM flashcards WHERE id = %s", (card_id,))
        if not card:
            return
        current_box = card[0]["box"]
        if correct:
            next_box = min(current_box + 1, 5)
        else:
            next_box = 1  # Reset to box 1 on failure
            
        from tse.utils.helpers import calculate_next_review
        next_review_time = calculate_next_review(next_box)
        
        self.execute_write(
            "UPDATE flashcards SET box = %s, next_review = %s WHERE id = %s",
            (next_box, next_review_time, card_id)
        )

    # Quiz helpers
    def add_quiz_question(self, question: str, opt_a: str, opt_b: str, opt_c: str, opt_d: str, correct: str, explanation: str, subject_id: Optional[int]) -> int:
        query = """
            INSERT INTO quizzes (question, option_a, option_b, option_c, option_d, correct_option, explanation, subject_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (question, opt_a, opt_b, opt_c, opt_d, correct, explanation, subject_id)
        return self.execute_write(query, params)

    def get_quizzes_by_subject(self, subject_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        # Check if we have quiz questions, if not, generate dynamically in CLI using LLM
        query = """
            SELECT q.id, q.question, q.option_a, q.option_b, q.option_c, q.option_d, q.correct_option, q.explanation, s.name as subject_name
            FROM quizzes q
            LEFT JOIN subjects s ON q.subject_id = s.id
            WHERE q.subject_id = %s
        """
        if self.is_sqlite:
            query += " ORDER BY RANDOM() LIMIT %s"
        else:
            query += " ORDER BY RAND() LIMIT %s"
        return self.execute_query(query, (subject_id, limit))

    def add_leaderboard_entry(self, user_name: str, score: int, subject_id: Optional[int]) -> int:
        query = """
            INSERT INTO leaderboard (user_name, score, subject_id, timestamp)
            VALUES (%s, %s, %s, %s)
        """
        return self.execute_write(query, (user_name, score, subject_id, datetime.now()))

    def get_leaderboard(self, subject_id: Optional[int] = None, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
            SELECT l.user_name, l.score, s.name as subject_name, l.timestamp
            FROM leaderboard l
            LEFT JOIN subjects s ON l.subject_id = s.id
            WHERE 1=1
        """
        params = []
        if subject_id:
            query += " AND l.subject_id = %s"
            params.append(subject_id)
        query += " ORDER BY l.score DESC, l.timestamp ASC LIMIT %s"
        params.append(limit)
        return self.execute_query(query, tuple(params))

    # Document Chunk helpers
    def add_document_chunk(self, doc_name: str, chunk_index: int, chunk_text: str) -> int:
        query = """
            INSERT INTO document_chunks (doc_name, chunk_index, chunk_text)
            VALUES (%s, %s, %s)
        """
        return self.execute_write(query, (doc_name, chunk_index, chunk_text))

    def get_document_chunk(self, doc_name: str, chunk_index: int) -> Optional[str]:
        query = "SELECT chunk_text FROM document_chunks WHERE doc_name = %s AND chunk_index = %s"
        res = self.execute_query(query, (doc_name, chunk_index))
        return res[0]["chunk_text"] if res else None

# Singleton DB instance
db = DatabaseManager()
