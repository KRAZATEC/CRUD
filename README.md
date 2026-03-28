# Task Manager — Cognifyz Tasks 3 & 5

A fully-featured **console-based Task Manager** implemented in Python, combining:
- **Task 3**: CRUD operations (Create, Read, Update, Delete) using a `Task` class and list-based storage
- **Task 5**: File I/O persistence using JSON, with error handling and TXT export

---

## Features

| Feature | Details |
|---------|---------|
| **CRUD** | Create, Read, Update, Delete tasks via interactive console menu |
| **File Persistence** | Auto-saves to `tasks.json` after every change |
| **Error Handling** | Handles missing files, corrupted JSON (auto-backup), permission errors |
| **Filtering** | Filter tasks by Status or Priority |
| **Search** | Keyword search across title and description |
| **Statistics** | Visual bar chart of tasks by status and priority |
| **TXT Export** | Export all tasks to a human-readable `.txt` file |
| **Test Suite** | 40+ unit & integration tests covering all requirements |

---

## Project Structure

```
task_manager/
├── task_manager.py        # Main application (Task, FileStorage, TaskManager, UI)
├── test_task_manager.py   # Comprehensive test suite
├── tasks.json             # Auto-created data file (after first run)
└── README.md              # This file
```

---

## How to Run

### Start the App
```bash
python task_manager.py
```

### Run Tests
```bash
python -m pytest test_task_manager.py -v
# or
python test_task_manager.py
```

---

## Architecture

### `Task` (Task 3 — Step 1)
Represents a single task with:
- `id` — auto-generated 8-char uppercase UUID
- `title`, `description`
- `priority` — Low / Medium / High / Critical
- `status` — Pending / In Progress / Completed / Cancelled
- `due_date`, `created_at`, `updated_at`
- `to_dict()` / `from_dict()` for serialization

### `FileStorage` (Task 5)
Handles all file I/O:
- `save(tasks)` — writes JSON with metadata
- `load()` — reads JSON, handles missing/corrupted files
- `export_txt(tasks, filename)` — human-readable export
- Auto-backup of corrupted files as `.bak`

### `TaskManager` (Task 3 — Steps 2–6)
Orchestrates CRUD:
- `create_task()` — validates and creates, auto-saves
- `read_all(filter_status, filter_priority)` — list with optional filters
- `read_by_id(id)` — lookup by ID
- `update_task(id, **kwargs)` — partial update, auto-saves
- `delete_task(id)` / `delete_all()` — removal, auto-saves
- `search(query)` — searches title + description
- `stats()` — count by status and priority

---

## Test Coverage

| Test Class | Covers |
|------------|--------|
| `TestTask` | Task attributes, validation, serialization |
| `TestFileStorage` | Save/load roundtrip, corruption handling, export |
| `TestTaskManagerCRUD` | All CRUD operations + persistence after each |
| `TestPersistenceScenarios` | Multi-session lifecycle, special characters, large datasets |

---

## Error Handling (Task 5 — Step 2)

| Scenario | Behavior |
|----------|----------|
| File not found | Returns empty list, creates new file on first save |
| Corrupted JSON | Returns empty list, backs up file as `.bak` |
| Permission denied | Prints error, returns False without crashing |
| Empty title | Raises `ValueError` with clear message |
| Invalid priority/status | Silently defaults to "Medium"/"Pending" |
| Non-existent task ID | Returns `None` or `False`, no crash |
