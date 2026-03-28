"""
Tests for Task Manager - CRUD + File Persistence
Covers Task 3 (CRUD) and Task 5 (File I/O) requirements
"""

import json
import os
import tempfile
import unittest
from datetime import datetime

# Import from task_manager.py
import sys
sys.path.insert(0, os.path.dirname(__file__))
from task_manager import Task, FileStorage, TaskManager


class TestTask(unittest.TestCase):
    """Tests for the Task class (Task 3 - Step 1: Define a Task class)."""

    def test_task_creation_with_defaults(self):
        task = Task("Buy groceries")
        self.assertEqual(task.title, "Buy groceries")
        self.assertEqual(task.priority, "Medium")
        self.assertEqual(task.status, "Pending")
        self.assertEqual(task.description, "")
        self.assertEqual(task.due_date, "")
        self.assertIsNotNone(task.id)
        self.assertIsNotNone(task.created_at)

    def test_task_creation_full(self):
        task = Task("Write report", "Quarterly report", "High", "In Progress", "2025-12-31")
        self.assertEqual(task.title, "Write report")
        self.assertEqual(task.description, "Quarterly report")
        self.assertEqual(task.priority, "High")
        self.assertEqual(task.status, "In Progress")
        self.assertEqual(task.due_date, "2025-12-31")

    def test_task_invalid_priority_defaults_to_medium(self):
        task = Task("Test", priority="SuperHigh")
        self.assertEqual(task.priority, "Medium")

    def test_task_invalid_status_defaults_to_pending(self):
        task = Task("Test", status="Deleted")
        self.assertEqual(task.status, "Pending")

    def test_task_to_dict(self):
        task = Task("Test task", "Desc", "Low", "Completed", "2025-01-01",
                    task_id="ABCD1234")
        d = task.to_dict()
        self.assertEqual(d["id"], "ABCD1234")
        self.assertEqual(d["title"], "Test task")
        self.assertEqual(d["description"], "Desc")
        self.assertEqual(d["priority"], "Low")
        self.assertEqual(d["status"], "Completed")
        self.assertEqual(d["due_date"], "2025-01-01")

    def test_task_from_dict(self):
        data = {
            "id": "XYZ99999",
            "title": "Roundtrip",
            "description": "Test",
            "priority": "Critical",
            "status": "Cancelled",
            "due_date": "2025-06-15",
            "created_at": "2025-01-01 00:00:00",
            "updated_at": "2025-01-01 00:00:00",
        }
        task = Task.from_dict(data)
        self.assertEqual(task.id, "XYZ99999")
        self.assertEqual(task.title, "Roundtrip")
        self.assertEqual(task.priority, "Critical")
        self.assertEqual(task.status, "Cancelled")

    def test_task_str(self):
        task = Task("My Task", priority="High", status="Pending", task_id="TST00001")
        s = str(task)
        self.assertIn("TST00001", s)
        self.assertIn("My Task", s)
        self.assertIn("High", s)


class TestFileStorage(unittest.TestCase):
    """Tests for FileStorage (Task 5 - File I/O + Error Handling)."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.filepath = os.path.join(self.tmpdir, "test_tasks.json")
        self.storage = FileStorage(self.filepath)

    def tearDown(self):
        for f in os.listdir(self.tmpdir):
            os.remove(os.path.join(self.tmpdir, f))
        os.rmdir(self.tmpdir)

    def _make_tasks(self, n=3):
        return [Task(f"Task {i}", f"Desc {i}", "Medium", "Pending") for i in range(1, n + 1)]

    def test_save_creates_file(self):
        tasks = self._make_tasks(2)
        result = self.storage.save(tasks)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.filepath))

    def test_save_and_load_roundtrip(self):
        tasks = self._make_tasks(3)
        self.storage.save(tasks)
        loaded = self.storage.load()
        self.assertEqual(len(loaded), 3)
        self.assertEqual(loaded[0].title, "Task 1")
        self.assertEqual(loaded[2].title, "Task 3")

    def test_load_missing_file_returns_empty(self):
        result = self.storage.load()
        self.assertEqual(result, [])

    def test_load_corrupted_file_returns_empty(self):
        with open(self.filepath, "w") as f:
            f.write("NOT VALID JSON {{{")
        result = self.storage.load()
        self.assertEqual(result, [])
        # Should create a backup
        self.assertTrue(os.path.exists(self.filepath + ".bak"))

    def test_save_empty_list(self):
        result = self.storage.save([])
        self.assertTrue(result)
        loaded = self.storage.load()
        self.assertEqual(loaded, [])

    def test_meta_fields_in_saved_file(self):
        tasks = self._make_tasks(2)
        self.storage.save(tasks)
        with open(self.filepath, "r") as f:
            data = json.load(f)
        self.assertIn("meta", data)
        self.assertEqual(data["meta"]["total_tasks"], 2)
        self.assertIn("version", data["meta"])
        self.assertIn("last_saved", data["meta"])

    def test_export_txt_creates_file(self):
        tasks = self._make_tasks(2)
        export_path = os.path.join(self.tmpdir, "export.txt")
        result = self.storage.export_txt(tasks, export_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(export_path))

    def test_export_txt_content(self):
        tasks = [Task("My Task", "My Desc", "High", "Pending", task_id="TEST0001")]
        export_path = os.path.join(self.tmpdir, "export.txt")
        self.storage.export_txt(tasks, export_path)
        with open(export_path, "r") as f:
            content = f.read()
        self.assertIn("My Task", content)
        self.assertIn("My Desc", content)
        self.assertIn("High", content)
        self.assertIn("TEST0001", content)

    def test_persistence_across_multiple_saves(self):
        tasks = self._make_tasks(2)
        self.storage.save(tasks)
        tasks.append(Task("Task 3"))
        self.storage.save(tasks)
        loaded = self.storage.load()
        self.assertEqual(len(loaded), 3)


class TestTaskManagerCRUD(unittest.TestCase):
    """Integration tests for TaskManager CRUD operations (Task 3 Steps 2–6)."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.filepath = os.path.join(self.tmpdir, "tasks.json")
        self.storage = FileStorage(self.filepath)
        self.manager = TaskManager(self.storage)

    def tearDown(self):
        for f in os.listdir(self.tmpdir):
            os.remove(os.path.join(self.tmpdir, f))
        os.rmdir(self.tmpdir)

    # ── CREATE ──────────────────────────────────────────────────────────────

    def test_create_task_basic(self):
        task = self.manager.create_task("Buy milk")
        self.assertEqual(task.title, "Buy milk")
        self.assertIn(task, self.manager.tasks)

    def test_create_task_all_fields(self):
        task = self.manager.create_task("Deploy app", "Staging first", "High", "In Progress", "2025-11-30")
        self.assertEqual(task.description, "Staging first")
        self.assertEqual(task.priority, "High")
        self.assertEqual(task.status, "In Progress")
        self.assertEqual(task.due_date, "2025-11-30")

    def test_create_task_empty_title_raises(self):
        with self.assertRaises(ValueError):
            self.manager.create_task("")

    def test_create_task_whitespace_title_raises(self):
        with self.assertRaises(ValueError):
            self.manager.create_task("   ")

    def test_create_task_auto_saves(self):
        self.manager.create_task("Persisted task")
        new_manager = TaskManager(FileStorage(self.filepath))
        self.assertEqual(len(new_manager.tasks), 1)
        self.assertEqual(new_manager.tasks[0].title, "Persisted task")

    def test_create_multiple_tasks_unique_ids(self):
        t1 = self.manager.create_task("Task A")
        t2 = self.manager.create_task("Task B")
        self.assertNotEqual(t1.id, t2.id)

    # ── READ ────────────────────────────────────────────────────────────────

    def test_read_all_empty(self):
        self.assertEqual(self.manager.read_all(), [])

    def test_read_all_returns_all_tasks(self):
        self.manager.create_task("A")
        self.manager.create_task("B")
        self.manager.create_task("C")
        self.assertEqual(len(self.manager.read_all()), 3)

    def test_read_by_id_found(self):
        task = self.manager.create_task("Find me")
        result = self.manager.read_by_id(task.id)
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "Find me")

    def test_read_by_id_not_found(self):
        result = self.manager.read_by_id("ZZZZZZZZ")
        self.assertIsNone(result)

    def test_filter_by_status(self):
        self.manager.create_task("T1", status="Pending")
        self.manager.create_task("T2", status="Completed")
        self.manager.create_task("T3", status="Pending")
        pending = self.manager.read_all(filter_status="Pending")
        self.assertEqual(len(pending), 2)
        completed = self.manager.read_all(filter_status="Completed")
        self.assertEqual(len(completed), 1)

    def test_filter_by_priority(self):
        self.manager.create_task("H1", priority="High")
        self.manager.create_task("H2", priority="High")
        self.manager.create_task("L1", priority="Low")
        high = self.manager.read_all(filter_priority="High")
        self.assertEqual(len(high), 2)

    def test_search_by_title(self):
        self.manager.create_task("Buy groceries")
        self.manager.create_task("Sell old stuff")
        self.manager.create_task("buy milk")
        results = self.manager.search("buy")
        self.assertEqual(len(results), 2)

    def test_search_by_description(self):
        self.manager.create_task("Task A", "Contains python code")
        self.manager.create_task("Task B", "Nothing special")
        results = self.manager.search("python")
        self.assertEqual(len(results), 1)

    def test_search_no_results(self):
        self.manager.create_task("Task X")
        results = self.manager.search("zzznomatch")
        self.assertEqual(results, [])

    # ── UPDATE ──────────────────────────────────────────────────────────────

    def test_update_title(self):
        task = self.manager.create_task("Old title")
        updated = self.manager.update_task(task.id, title="New title")
        self.assertEqual(updated.title, "New title")

    def test_update_status(self):
        task = self.manager.create_task("A task")
        self.manager.update_task(task.id, status="Completed")
        self.assertEqual(self.manager.read_by_id(task.id).status, "Completed")

    def test_update_priority(self):
        task = self.manager.create_task("A task")
        self.manager.update_task(task.id, priority="Critical")
        self.assertEqual(self.manager.read_by_id(task.id).priority, "Critical")

    def test_update_multiple_fields(self):
        task = self.manager.create_task("Orig", "Orig desc", "Low", "Pending")
        self.manager.update_task(task.id, title="Updated", priority="High", status="In Progress")
        t = self.manager.read_by_id(task.id)
        self.assertEqual(t.title, "Updated")
        self.assertEqual(t.priority, "High")
        self.assertEqual(t.status, "In Progress")

    def test_update_nonexistent_returns_none(self):
        result = self.manager.update_task("FAKEIDXX", title="Ghost")
        self.assertIsNone(result)

    def test_update_sets_updated_at(self):
        task = self.manager.create_task("Time check")
        old_time = task.updated_at
        import time; time.sleep(1)
        self.manager.update_task(task.id, status="Completed")
        updated = self.manager.read_by_id(task.id)
        self.assertGreaterEqual(updated.updated_at, old_time)

    def test_update_persisted_to_file(self):
        task = self.manager.create_task("Persist me")
        self.manager.update_task(task.id, title="Persisted Update", status="Completed")
        new_manager = TaskManager(FileStorage(self.filepath))
        reloaded = new_manager.read_by_id(task.id)
        self.assertEqual(reloaded.title, "Persisted Update")
        self.assertEqual(reloaded.status, "Completed")

    # ── DELETE ──────────────────────────────────────────────────────────────

    def test_delete_task(self):
        task = self.manager.create_task("Delete me")
        result = self.manager.delete_task(task.id)
        self.assertTrue(result)
        self.assertIsNone(self.manager.read_by_id(task.id))

    def test_delete_nonexistent_returns_false(self):
        result = self.manager.delete_task("NOTEXIST")
        self.assertFalse(result)

    def test_delete_reduces_count(self):
        t1 = self.manager.create_task("Keep")
        t2 = self.manager.create_task("Remove")
        self.manager.delete_task(t2.id)
        self.assertEqual(len(self.manager.tasks), 1)
        self.assertEqual(self.manager.tasks[0].id, t1.id)

    def test_delete_persisted_to_file(self):
        task = self.manager.create_task("Will be deleted")
        self.manager.delete_task(task.id)
        new_manager = TaskManager(FileStorage(self.filepath))
        self.assertEqual(len(new_manager.tasks), 0)

    def test_delete_all(self):
        for i in range(5):
            self.manager.create_task(f"Task {i}")
        count = self.manager.delete_all()
        self.assertEqual(count, 5)
        self.assertEqual(len(self.manager.tasks), 0)

    # ── STATS ───────────────────────────────────────────────────────────────

    def test_stats_empty(self):
        stats = self.manager.stats()
        self.assertEqual(stats["total"], 0)

    def test_stats_counts(self):
        self.manager.create_task("A", status="Pending")
        self.manager.create_task("B", status="Pending")
        self.manager.create_task("C", status="Completed")
        stats = self.manager.stats()
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["by_status"]["Pending"], 2)
        self.assertEqual(stats["by_status"]["Completed"], 1)


class TestPersistenceScenarios(unittest.TestCase):
    """End-to-end persistence tests (Task 5 - Step 3: Test persistence)."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.filepath = os.path.join(self.tmpdir, "persist.json")

    def tearDown(self):
        for f in os.listdir(self.tmpdir):
            os.remove(os.path.join(self.tmpdir, f))
        os.rmdir(self.tmpdir)

    def new_manager(self):
        return TaskManager(FileStorage(self.filepath))

    def test_full_lifecycle_across_sessions(self):
        """Simulate multiple app sessions with full CRUD + persistence."""
        # Session 1: Create tasks
        m1 = self.new_manager()
        t1 = m1.create_task("Alpha", "First task", "High", "Pending", "2025-01-01")
        t2 = m1.create_task("Beta", "Second task", "Low", "In Progress")
        m1.create_task("Gamma", "Third task", "Medium", "Completed")

        # Session 2: Read and update
        m2 = self.new_manager()
        self.assertEqual(len(m2.tasks), 3)
        m2.update_task(t1.id, status="Completed", priority="Critical")
        m2.delete_task(t2.id)

        # Session 3: Verify final state
        m3 = self.new_manager()
        self.assertEqual(len(m3.tasks), 2)
        alpha = m3.read_by_id(t1.id)
        self.assertEqual(alpha.status, "Completed")
        self.assertEqual(alpha.priority, "Critical")
        self.assertIsNone(m3.read_by_id(t2.id))

    def test_data_integrity_special_characters(self):
        m = self.new_manager()
        m.create_task("Tâche spéciale", "Données avec accents: é, ü, ñ, 中文")
        reloaded = self.new_manager()
        self.assertIn("é", reloaded.tasks[0].description)
        self.assertIn("中文", reloaded.tasks[0].description)

    def test_large_dataset_persistence(self):
        m = self.new_manager()
        for i in range(100):
            m.create_task(f"Task {i:03d}", f"Description {i}", "Medium", "Pending")
        reloaded = self.new_manager()
        self.assertEqual(len(reloaded.tasks), 100)


if __name__ == "__main__":
    print("=" * 60)
    print("  TASK MANAGER - TEST SUITE")
    print("=" * 60)
    unittest.main(verbosity=2)
