import unittest
import sqlite3
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from examai.database import DatabaseManager

class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Sets up a database manager running with a temporary SQLite file."""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = Path(self.test_dir) / "test_examai.db"
        
        self.db = DatabaseManager()
        self.db.is_sqlite = True
        
        # Override connection method to return the temporary file db connection
        def mock_connection():
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            return conn, True
            
        self.db.get_connection = mock_connection
        self.db.init_db()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_subjects_prepopulation(self):
        """Verifies subjects are pre-populated on init."""
        subjects = self.db.get_subjects()
        self.assertTrue(len(subjects) > 0)
        self.assertIn("DBMS", [s["name"] for s in subjects])

    def test_history_creation_and_retrieval(self):
        """Tests adding and fetching question history."""
        # Get DBMS subject ID
        subject = self.db.get_subject_by_name("DBMS")
        self.assertIsNotNone(subject)
        
        # Add history entry
        question = "What is database normalization?"
        answer = "Normalization is the process of organizing data to reduce redundancy."
        hist_id = self.db.add_history(question, answer, subject["id"], "theory", 5, "normalization,dbms")
        self.assertTrue(hist_id > 0)
        
        # Retrieve history
        history = self.db.get_history(subject_id=subject["id"])
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["question"], question)
        self.assertEqual(history[0]["favorite"], 0)

        # Toggle favorite bookmark
        new_state = self.db.toggle_favorite(hist_id)
        self.assertTrue(new_state)
        
        # Verify bookmark retrieval
        bookmarks = self.db.get_bookmarks()
        self.assertEqual(len(bookmarks), 1)
        self.assertEqual(bookmarks[0]["question"], question)

    def test_flashcards_spaced_repetition(self):
        """Tests adding and updating flashcards with Leitner scheduling."""
        subject = self.db.get_subject_by_name("Operating Systems")
        self.assertIsNotNone(subject)
        
        # Add flashcard
        card_id = self.db.add_flashcard("What is paging?", "Memory management scheme", subject["id"])
        self.assertTrue(card_id > 0)
        
        # Retrieve due flashcards (due immediately on creation)
        due_cards = self.db.get_due_flashcards(subject["id"])
        self.assertEqual(len(due_cards), 1)
        self.assertEqual(due_cards[0]["question"], "What is paging?")
        self.assertEqual(due_cards[0]["box"], 1)
        
        # Review card correctly (moves to box 2)
        self.db.update_flashcard_leitner(card_id, correct=True)
        
        # Fetch individual card to check new box
        cards = self.db.execute_query("SELECT box FROM flashcards WHERE id = %s", (card_id,))
        self.assertEqual(cards[0]["box"], 2)

    def test_quizzes_and_leaderboard(self):
        """Tests quiz management and score leaderboards."""
        subject = self.db.get_subject_by_name("DAA")
        self.assertIsNotNone(subject)
        
        # Add quiz question
        q_id = self.db.add_quiz_question(
            question="What is the time complexity of Quick Sort in average case?",
            opt_a="O(N)", opt_b="O(N^2)", opt_c="O(N log N)", opt_d="O(log N)",
            correct="C", explanation="Average case sorting time is linearithmic.",
            subject_id=subject["id"]
        )
        self.assertTrue(q_id > 0)
        
        # Fetch quiz
        quizzes = self.db.get_quizzes_by_subject(subject["id"], limit=5)
        self.assertEqual(len(quizzes), 1)
        self.assertEqual(quizzes[0]["correct_option"], "C")
        
        # Add leaderboard score
        self.db.add_leaderboard_entry("Alice", 4, subject["id"])
        self.db.add_leaderboard_entry("Bob", 5, subject["id"])
        
        # Verify rankings
        leaderboard = self.db.get_leaderboard(subject["id"])
        self.assertEqual(len(leaderboard), 2)
        # Bob has 5/5, so he must be first
        self.assertEqual(leaderboard[0]["user_name"], "Bob")
