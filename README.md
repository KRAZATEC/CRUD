# Task Manager (CRUD with JSON Storage)

A clean **Python Task Manager** that demonstrates end‑to‑end CRUD operations, JSON‑based persistence, and robust error handling, built as part of Cognifyz Tasks 3 & 5. [page:1]

---

## 📌 Features

- Full **CRUD**: Create, read, update, and delete tasks from an interactive console. [page:1]  
- **JSON persistence**: All tasks are stored in `tasks.json`, auto‑saved after each change. [page:1]  
- **Safe file I/O**: Handles missing files, corrupted JSON (with `.bak` backup), and permission errors. [page:1]  
- **Filtering & search**: Filter by status or priority, or search by keywords. [page:1]  
- **Task statistics**: Get counts by status and priority for quick overview. [page:1]  
- **TXT export**: Export tasks to a readable `.txt` file for sharing/backup. [page:1]  
- **Tests included**: Unit and integration tests for `Task`, `FileStorage`, and `TaskManager`. [page:1]

---

## 🛠 Tech Stack

- **Language**: Python 3.x [page:1]  
- **Storage**: JSON (`tasks.json`) [page:1]  
- **Testing**: `pytest` / `unittest` via `test_task_manager.py` [page:1]

---

## 📂 Project Structure

```text
.
├── task_manager.py       # Core logic: Task, FileStorage, TaskManager, CLI menu
├── test_task_manager.py  # Test suite
├── tasks.json            # Data file (auto-created on first save)
└── README.md             # Project documentation
```
[page:1]

If present in your repo, you can also add:

```text
streamlit_app.py          # Optional Streamlit UI wrapper (future enhancement)
```
[page:1]

---

## ✅ Core Concepts

### Task

Represents a single task with validation and timestamps. [page:1]

- `id`: 8‑character uppercase UUID. [page:1]  
- `title`, `description`: Main task content. [page:1]  
- `priority`: `Low`, `Medium`, `High`, `Critical`. [page:1]  
- `status`: `Pending`, `In Progress`, `Completed`, `Cancelled`. [page:1]  
- Dates: `due_date`, `created_at`, `updated_at`. [page:1]  
- Methods: `to_dict()`, `from_dict()` for JSON serialization. [page:1]

### FileStorage

Handles all file operations. [page:1]

- `save(tasks)`: Writes task list to JSON with metadata. [page:1]  
- `load()`: Reads tasks from JSON, recovering from missing or corrupted files. [page:1]  
- `export_txt(tasks, filename)`: Writes a human‑readable task list to `.txt`. [page:1]  
- On JSON corruption, creates a `.bak` backup and starts with an empty list. [page:1]

### TaskManager

High‑level manager around `Task` and `FileStorage`. [page:1]

- `create_task(...)`  
- `read_all(filter_status=None, filter_priority=None)`  
- `read_by_id(task_id)`  
- `update_task(task_id, **kwargs)`  
- `delete_task(task_id)` and `delete_all()`  
- `search(query)`  
- `stats()` – counts by status and priority. [page:1]

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/KRAZATEC/CRUD.git
cd CRUD
```
[page:1]

### 2. (Optional) Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
```

### 3. Run the console app

```bash
python task_manager.py
```

The script will start an interactive menu and create `tasks.json` on first save. [page:1]

---

## 🧪 Running Tests

```bash
# Using pytest (recommended)
python -m pytest test_task_manager.py -v

# Or plain Python
python test_task_manager.py
```
[page:1]

---

## 🔮 Future Improvements

- Build a **Streamlit** or web UI on top of `TaskManager`. [page:1]  
- Add CSV export for spreadsheet analysis.  
- Switch from JSON to SQLite/PostgreSQL for multi‑user scenarios.  

---

## 📄 License

This project is currently unlicensed.  
You can add a `LICENSE` file (for example MIT) if you want others to use it freely.
