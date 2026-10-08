# Library Manager (Django, sample data)

A small Django website for browsing books and members, searching, borrowing
and returning books, member history and statistics. Data lives in Python
lists in `library/sample_data.py` (no database); changes reset on restart.

## Setup

```
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py runserver
```

Open http://127.0.0.1:8000/