# Attendance Management System

This is a simple attendance management system built with Django.

## Features

- User registration and login
- Attendance marking (check-in and check-out)
- User dashboard to view recent attendance records
- Admin interface for managing attendance records

## Setup Instructions

1. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On macOS/Linux
```

2. Install dependencies:

```bash
pip install django
```

3. Run migrations:

```bash
python manage.py migrate
```

4. Create a superuser (admin):

```bash
python manage.py createsuperuser
```

5. Run the development server:

```bash
python manage.py runserver
```

6. Open your browser and go to `http://127.0.0.1:8000/`

## Usage

- Register a new user or login with an existing account.
- Mark attendance by checking in and checking out.
- Admin can manage attendance records via the Django admin interface at `/admin`.
