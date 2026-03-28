"""
Task Manager - Full CRUD Application with File Persistence
Cognifyz Task 3 + Task 5 Combined Implementation
"""

import json
import os
import uuid
from datetime import datetime
from typing import Optional


TASKS_FILE = "tasks.json"


class Task:
    """Represents a single task with all attributes."""

    PRIORITIES = ["Low", "Medium", "High", "Critical"]
    STATUSES = ["Pending", "In Progress", "Completed", "Cancelled"]

    def __init__(
        self,
        title: str,
        description: str = "",
        priority: str = "Medium",
        status: str = "Pending",
        due_date: str = "",
        task_id: str = None,
        created_at: str = None,
        updated_at: str = None,
    ):
        self.id = task_id or str(uuid.uuid4())[:8].upper()
        self.title = title
        self.description = description
        self.priority = priority if priority in self.PRIORITIES else "Medium"
        self.status = status if status in self.STATUSES else "Pending"
        self.due_date = due_date
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = updated_at or self.created_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "due_date": self.due_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            title=data["title"],
            description=data.get("description", ""),
            priority=data.get("priority", "Medium"),
            status=data.get("status", "Pending"),
            due_date=data.get("due_date", ""),
            task_id=data.get("id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def __str__(self) -> str:
        return (
            f"[{self.id}] {self.title} | {self.priority} | {self.status}"
            + (f" | Due: {self.due_date}" if self.due_date else "")
        )


class FileStorage:
    """Handles persistent storage of tasks using JSON file I/O."""

    def __init__(self, filepath: str = TASKS_FILE):
        self.filepath = filepath

    def save(self, tasks: list[Task]) -> bool:
        """Save all tasks to the JSON file."""
        try:
            data = {
                "meta": {
                    "version": "1.0",
                    "last_saved": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total_tasks": len(tasks),
                },
                "tasks": [task.to_dict() for task in tasks],
            }
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except PermissionError:
            print(f"  [ERROR] Permission denied writing to '{self.filepath}'.")
            return False
        except OSError as e:
            print(f"  [ERROR] Could not save tasks: {e}")
            return False

    def load(self) -> list[Task]:
        """Load tasks from the JSON file."""
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            tasks_data = data.get("tasks", [])
            return [Task.from_dict(t) for t in tasks_data]
        except json.JSONDecodeError:
            print(f"  [WARNING] '{self.filepath}' is corrupted. Starting fresh.")
            self._backup_corrupted_file()
            return []
        except KeyError as e:
            print(f"  [WARNING] Missing field {e} in task data. Some tasks may be skipped.")
            return []
        except OSError as e:
            print(f"  [ERROR] Could not read tasks file: {e}")
            return []

    def _backup_corrupted_file(self):
        backup = self.filepath + ".bak"
        try:
            os.rename(self.filepath, backup)
            print(f"  [INFO] Corrupted file backed up as '{backup}'.")
        except OSError:
            pass

    def export_txt(self, tasks: list[Task], filename: str = "tasks_export.txt") -> bool:
        """Export tasks to a human-readable text file."""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                f.write("       TASK MANAGER - EXPORTED TASKS\n")
                f.write(f"       Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                if not tasks:
                    f.write("No tasks found.\n")
                else:
                    for i, task in enumerate(tasks, 1):
                        f.write(f"Task #{i}\n")
                        f.write(f"  ID         : {task.id}\n")
                        f.write(f"  Title      : {task.title}\n")
                        f.write(f"  Description: {task.description or 'N/A'}\n")
                        f.write(f"  Priority   : {task.priority}\n")
                        f.write(f"  Status     : {task.status}\n")
                        f.write(f"  Due Date   : {task.due_date or 'N/A'}\n")
                        f.write(f"  Created    : {task.created_at}\n")
                        f.write(f"  Updated    : {task.updated_at}\n")
                        f.write("-" * 40 + "\n")
                f.write(f"\nTotal: {len(tasks)} task(s)\n")
            return True
        except OSError as e:
            print(f"  [ERROR] Export failed: {e}")
            return False


class TaskManager:
    """Core manager: CRUD operations on tasks with file persistence."""

    def __init__(self, storage: FileStorage):
        self.storage = storage
        self.tasks: list[Task] = storage.load()
        print(f"  [INFO] Loaded {len(self.tasks)} task(s) from '{storage.filepath}'.")

    def create_task(self, title: str, description: str = "", priority: str = "Medium",
                    status: str = "Pending", due_date: str = "") -> Task:
        if not title.strip():
            raise ValueError("Task title cannot be empty.")
        task = Task(title.strip(), description.strip(), priority, status, due_date.strip())
        self.tasks.append(task)
        self._auto_save()
        return task

    def read_all(self, filter_status: str = None, filter_priority: str = None) -> list[Task]:
        result = self.tasks
        if filter_status:
            result = [t for t in result if t.status.lower() == filter_status.lower()]
        if filter_priority:
            result = [t for t in result if t.priority.lower() == filter_priority.lower()]
        return result

    def read_by_id(self, task_id: str) -> Optional[Task]:
        return next((t for t in self.tasks if t.id == task_id.upper()), None)

    def update_task(self, task_id: str, **kwargs) -> Optional[Task]:
        task = self.read_by_id(task_id)
        if not task:
            return None
        if "title" in kwargs and kwargs["title"].strip():
            task.title = kwargs["title"].strip()
        if "description" in kwargs:
            task.description = kwargs["description"].strip()
        if "priority" in kwargs and kwargs["priority"] in Task.PRIORITIES:
            task.priority = kwargs["priority"]
        if "status" in kwargs and kwargs["status"] in Task.STATUSES:
            task.status = kwargs["status"]
        if "due_date" in kwargs:
            task.due_date = kwargs["due_date"].strip()
        task.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._auto_save()
        return task

    def delete_task(self, task_id: str) -> bool:
        task = self.read_by_id(task_id)
        if task:
            self.tasks.remove(task)
            self._auto_save()
            return True
        return False

    def delete_all(self) -> int:
        count = len(self.tasks)
        self.tasks.clear()
        self._auto_save()
        return count

    def search(self, query: str) -> list[Task]:
        q = query.lower()
        return [t for t in self.tasks if q in t.title.lower() or q in t.description.lower()]

    def stats(self) -> dict:
        total = len(self.tasks)
        by_status = {s: sum(1 for t in self.tasks if t.status == s) for s in Task.STATUSES}
        by_priority = {p: sum(1 for t in self.tasks if t.priority == p) for p in Task.PRIORITIES}
        return {"total": total, "by_status": by_status, "by_priority": by_priority}

    def _auto_save(self):
        self.storage.save(self.tasks)


# ─────────────────────────────────────────────
#  Colorful Console UI
# ─────────────────────────────────────────────

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    print(f"{Colors.CYAN}{Colors.BOLD}\n" + "═" * 60)
    print("        ✦  TASK MANAGER  ✦   (Cognifyz Tasks 3 & 5)")
    print("═" * 60 + f"{Colors.ENDC}")

def pause():
    input(f"\n{Colors.BLUE}  Press Enter to continue...{Colors.ENDC}")

def choose(options: list, label: str) -> str:
    print(f"\n{Colors.HEADER}  {label}:{Colors.ENDC}")
    for i, opt in enumerate(options, 1):
        print(f"{Colors.GREEN}    {i}. {opt}{Colors.ENDC}")
    while True:
        raw = input(f"{Colors.CYAN}  Choice (number): {Colors.ENDC}").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print(f"{Colors.RED}  Invalid choice. Try again.{Colors.ENDC}")

def display_tasks(tasks: list[Task]):
    if not tasks:
        print(f"\n{Colors.YELLOW}  No tasks found.{Colors.ENDC}")
        return
    print()
    print(f"{Colors.BOLD}{Colors.HEADER}  {'ID':<10} {'TITLE':<28} {'PRIORITY':<10} {'STATUS':<14} {'DUE DATE'}{Colors.ENDC}")
    print(f"{Colors.HEADER}  " + "─" * 78 + f"{Colors.ENDC}")
    for t in tasks:
        title = t.title[:26] + ".." if len(t.title) > 26 else t.title
        
        # Colorize priority
        p_color = Colors.RED if t.priority == "Critical" else (Colors.YELLOW if t.priority == "High" else (Colors.BLUE if t.priority == "Medium" else Colors.GREEN))
        
        # Colorize status
        s_color = Colors.GREEN if t.status == "Completed" else (Colors.CYAN if t.status == "In Progress" else (Colors.RED if t.status == "Cancelled" else Colors.YELLOW))
        
        print(f"  {Colors.BOLD}{t.id:<10}{Colors.ENDC} {title:<28} {p_color}{t.priority:<10}{Colors.ENDC} {s_color}{t.status:<14}{Colors.ENDC} {t.due_date or '—'}")
    print(f"\n{Colors.BLUE}  Total: {len(tasks)} task(s){Colors.ENDC}")


def menu_create(manager: TaskManager):
    print(f"\n{Colors.HEADER}{Colors.BOLD}  ── CREATE TASK ──{Colors.ENDC}")
    title = input(f"{Colors.CYAN}  Title*: {Colors.ENDC}").strip()
    if not title:
        print(f"{Colors.RED}  [!] Title is required.{Colors.ENDC}")
        return
    description = input(f"{Colors.CYAN}  Description (optional): {Colors.ENDC}")
    priority = choose(Task.PRIORITIES, "Priority")
    status = choose(Task.STATUSES, "Status")
    due_date = input(f"{Colors.CYAN}  Due Date (YYYY-MM-DD, optional): {Colors.ENDC}").strip()
    try:
        task = manager.create_task(title, description, priority, status, due_date)
        print(f"\n{Colors.GREEN}  ✔ Task created: {task}{Colors.ENDC}")
    except ValueError as e:
        print(f"\n{Colors.RED}  [ERROR] {e}{Colors.ENDC}")


def menu_read(manager: TaskManager):
    print(f"\n{Colors.HEADER}{Colors.BOLD}  ── VIEW TASKS ──{Colors.ENDC}")
    sub = choose(["All tasks", "Filter by status", "Filter by priority", "Search by keyword"], "View")
    if sub == "All tasks":
        display_tasks(manager.read_all())
    elif sub == "Filter by status":
        status = choose(Task.STATUSES, "Status")
        display_tasks(manager.read_all(filter_status=status))
    elif sub == "Filter by priority":
        priority = choose(Task.PRIORITIES, "Priority")
        display_tasks(manager.read_all(filter_priority=priority))
    else:
        query = input(f"{Colors.CYAN}  Search keyword: {Colors.ENDC}").strip()
        results = manager.search(query)
        print(f"\n{Colors.GREEN}  Results for '{query}':{Colors.ENDC}")
        display_tasks(results)


def menu_update(manager: TaskManager):
    print(f"\n{Colors.HEADER}{Colors.BOLD}  ── UPDATE TASK ──{Colors.ENDC}")
    display_tasks(manager.read_all())
    task_id = input(f"\n{Colors.CYAN}  Enter Task ID to update: {Colors.ENDC}").strip().upper()
    task = manager.read_by_id(task_id)
    if not task:
        print(f"{Colors.RED}  [!] No task with ID '{task_id}'.{Colors.ENDC}")
        return
    print(f"\n{Colors.GREEN}  Updating: {task}{Colors.ENDC}")
    print(f"{Colors.YELLOW}  (Leave blank to keep current value){Colors.ENDC}")
    title = input(f"{Colors.CYAN}  Title [{task.title}]: {Colors.ENDC}").strip()
    description = input(f"{Colors.CYAN}  Description [{task.description or '—'}]: {Colors.ENDC}")
    priority = choose(Task.PRIORITIES + ["Keep current"], f"Priority [{task.priority}]")
    status = choose(Task.STATUSES + ["Keep current"], f"Status [{task.status}]")
    due_date = input(f"{Colors.CYAN}  Due Date [{task.due_date or '—'}]: {Colors.ENDC}").strip()

    updates = {}
    if title: updates["title"] = title
    if description: updates["description"] = description
    if priority != "Keep current": updates["priority"] = priority
    if status != "Keep current": updates["status"] = status
    if due_date: updates["due_date"] = due_date

    updated = manager.update_task(task_id, **updates)
    if updated:
        print(f"\n{Colors.GREEN}  ✔ Updated: {updated}{Colors.ENDC}")
    else:
        print(f"{Colors.RED}  [!] Update failed.{Colors.ENDC}")


def menu_delete(manager: TaskManager):
    print(f"\n{Colors.HEADER}{Colors.BOLD}  ── DELETE TASK ──{Colors.ENDC}")
    sub = choose(["Delete specific task", "Delete all tasks"], "Delete")
    if sub == "Delete all tasks":
        confirm = input(f"{Colors.RED}  Are you sure? This deletes ALL tasks. (yes/no): {Colors.ENDC}").strip().lower()
        if confirm == "yes":
            count = manager.delete_all()
            print(f"\n{Colors.GREEN}  ✔ Deleted {count} task(s).{Colors.ENDC}")
        else:
            print(f"{Colors.YELLOW}  Cancelled.{Colors.ENDC}")
        return

    display_tasks(manager.read_all())
    task_id = input(f"\n{Colors.CYAN}  Enter Task ID to delete: {Colors.ENDC}").strip().upper()
    task = manager.read_by_id(task_id)
    if not task:
        print(f"{Colors.RED}  [!] No task with ID '{task_id}'.{Colors.ENDC}")
        return
    confirm = input(f"{Colors.RED}  Delete '{task.title}'? (yes/no): {Colors.ENDC}").strip().lower()
    if confirm == "yes":
        manager.delete_task(task_id)
        print(f"{Colors.GREEN}  ✔ Task deleted.{Colors.ENDC}")
    else:
        print(f"{Colors.YELLOW}  Cancelled.{Colors.ENDC}")


def menu_stats(manager: TaskManager):
    stats = manager.stats()
    print(f"\n{Colors.HEADER}{Colors.BOLD}  ── STATISTICS ──{Colors.ENDC}")
    print(f"\n{Colors.CYAN}  Total Tasks : {stats['total']}{Colors.ENDC}")
    print(f"\n{Colors.BLUE}  By Status:{Colors.ENDC}")
    for s, c in stats["by_status"].items():
        bar = "█" * c + "░" * max(0, 10 - c)
        print(f"{Colors.GREEN}    {s:<14} {bar}  {c}{Colors.ENDC}")
    print(f"\n{Colors.BLUE}  By Priority:{Colors.ENDC}")
    for p, c in stats["by_priority"].items():
        bar = "█" * c + "░" * max(0, 10 - c)
        print(f"{Colors.YELLOW}    {p:<14} {bar}  {c}{Colors.ENDC}")


def menu_export(manager: TaskManager):
    print(f"\n{Colors.HEADER}{Colors.BOLD}  ── EXPORT TASKS ──{Colors.ENDC}")
    filename = input(f"{Colors.CYAN}  Export filename [tasks_export.txt]: {Colors.ENDC}").strip() or "tasks_export.txt"
    if not filename.endswith(".txt"):
        filename += ".txt"
    ok = manager.storage.export_txt(manager.tasks, filename)
    if ok:
        print(f"{Colors.GREEN}  ✔ Tasks exported to '{filename}'.{Colors.ENDC}")
    else:
        print(f"{Colors.RED}  [!] Export failed.{Colors.ENDC}")


def main():
    storage = FileStorage(TASKS_FILE)
    manager = TaskManager(storage)

    MENU = [
        "Create task",
        "View / Search tasks",
        "Update task",
        "Delete task",
        "Statistics",
        "Export to TXT",
        "Exit",
    ]

    # Ensure windows terminal supports ANSI colors
    if os.name == 'nt':
        os.system('')

    while True:
        clear()
        banner()
        stats = manager.stats()
        print(f"{Colors.CYAN}  Tasks: {stats['total']} total | "
              f"{Colors.YELLOW}Pending: {stats['by_status']['Pending']} | "
              f"{Colors.BLUE}In Progress: {stats['by_status']['In Progress']} | "
              f"{Colors.GREEN}Done: {stats['by_status']['Completed']}{Colors.ENDC}")
        print()
        for i, item in enumerate(MENU, 1):
            print(f"{Colors.GREEN}  {i}. {item}{Colors.ENDC}")
        print()
        choice = input(f"{Colors.CYAN}  Select option: {Colors.ENDC}").strip()

        if not choice.isdigit() or not (1 <= int(choice) <= len(MENU)):
            print(f"{Colors.RED}  Invalid option.{Colors.ENDC}")
            pause()
            continue

        idx = int(choice)
        if idx == 1:
            menu_create(manager)
        elif idx == 2:
            menu_read(manager)
        elif idx == 3:
            menu_update(manager)
        elif idx == 4:
            menu_delete(manager)
        elif idx == 5:
            menu_stats(manager)
        elif idx == 6:
            menu_export(manager)
        elif idx == 7:
            print(f"\n{Colors.GREEN}{Colors.BOLD}  Goodbye! All tasks saved. ✔\n{Colors.ENDC}")
            break

        if idx != 7:
            pause()


if __name__ == "__main__":
    main()
