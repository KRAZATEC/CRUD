Task Manager – CRUD with JSON Persistence
A fully-featured Python Task Manager that demonstrates clean CRUD design, JSON-based persistence, and a small but complete test suite.

This project was built as part of Cognifyz Tasks 3 & 5, combining console CRUD operations with robust file I/O and error handling.

Features
Full CRUD: Create, read, update, and delete tasks from an interactive console menu.

JSON persistence: All changes are auto-saved to tasks.json after every operation.

Resilient file I/O: Handles missing files, corrupted JSON (with .bak backup), and permission issues gracefully.

Filtering and search: Filter by status or priority, or search by keywords in title/description.

Statistics view: Get counts of tasks by status and priority, suitable for a simple bar-chart style summary.

TXT export: Export tasks to a human-readable .txt file for sharing or backup.

Test suite: 40+ unit and integration tests covering Task, FileStorage, and TaskManager behavior.

Tech Stack
Language: Python 3.x

Data format: JSON (tasks.json) for persistence

Testing: pytest or plain python test_task_manager.py

Project Structure
text
.
├── streamlit_app.py        # (Optional) Streamlit UI wrapper (if used)
├── task_manager.py         # Core logic: Task, FileStorage, TaskManager, CLI
├── test_task_manager.py    # Test suite
├── tasks.json              # Auto-created data file on first save
└── README.md               # Project documentation
Core Components
Task
Represents a single task with metadata and validation.

id: Auto-generated 8-character uppercase UUID.

title, description: Basic task details.

priority: One of Low / Medium / High / Critical.

status: One of Pending / In Progress / Completed / Cancelled.

Timestamps: due_date, created_at, updated_at.

Serialization helpers: to_dict() and from_dict().

FileStorage
Encapsulates all file I/O.

save(tasks): Writes JSON to disk with metadata.

load(): Reads and parses JSON, handling missing or corrupted files.

export_txt(tasks, filename): Exports tasks to a readable .txt file.

On corrupted JSON, creates a .bak backup and starts from an empty list.

TaskManager
Coordinates all higher-level operations.

create_task(...): Validates input, creates a task, and auto-saves.

read_all(filter_status=None, filter_priority=None): Lists tasks with optional filters.

read_by_id(task_id): Looks up a task by its ID.

update_task(task_id, **kwargs): Partially updates a task and saves.

delete_task(task_id) / delete_all(): Deletes one or all tasks.

search(query): Keyword search over title and description.

stats(): Returns aggregated counts by status and priority.

Error Handling
This project is designed to fail safe rather than crash.

File not found: Returns an empty list, creates tasks.json on first save.

Corrupted JSON: Backs up the corrupted file as .bak and starts fresh.

Permission denied: Logs a clear error and returns False instead of crashing.

Empty title: Raises ValueError with a descriptive message.

Invalid priority/status: Falls back to default "Medium" / "Pending".

Unknown task ID: Returns None or False for lookups/operations.

Getting Started
Prerequisites
Python 3.8+ installed.

Recommended: virtual environment (venv) for isolation.

Clone the repository
bash
git clone https://github.com/KRAZATEC/CRUD.git
cd CRUD
Run the console app
bash
python task_manager.py
This will start the interactive menu and create tasks.json automatically on first save.

Running Tests
You can run the tests either via pytest or directly with Python.

bash
# Using pytest
python -m pytest test_task_manager.py -v

# Or directly
python test_task_manager.py
Possible Extensions
Add a richer Streamlit UI using streamlit_app.py.

Add export to CSV for usage in spreadsheets or BI tools.

Integrate with a database (SQLite/PostgreSQL) instead of JSON for multi-user scenarios.

License
Add your preferred license here (e.g., MIT), and include a LICENSE file in the repository.
