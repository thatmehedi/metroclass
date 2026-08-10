# MetroClass

> A modern Classroom Management System built with Django.

[Open the Live Demo](https://thatmehedi.pythonanywhere.com)

MetroClass helps teachers manage courses, announcements, lectures, assignments, and student submissions in one clean workspace. It is inspired by classroom-learning platforms while using its own MetroClass design and workflow.

## Features

### Students

- Register, sign in, and manage account settings
- Join and leave courses
- View course announcements and lectures
- View assignments and submit work
- Track upcoming assignment deadlines

### Teachers

- Create, edit, archive, and delete courses
- Organize courses by batch or group
- Post and manage announcements
- Upload lecture files or share external links
- Create assignments and review student submissions

## Technology Stack

- Python
- Django
- HTML
- CSS
- JavaScript
- Bootstrap 5
- SQLite (development and demo deployment)

## Run Locally

```bash
git clone https://github.com/thatmehedi/metroclass.git
cd metroclass
python -m venv venv
```

Activate the virtual environment, then install packages:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

## Project Structure

```text
metroclass/
├── accounts/      # Authentication, profiles, dashboards
├── courses/       # Courses, announcements, lectures, assignments
├── core/          # Home page, shared static files, styling
├── metroclass/    # Django project configuration
└── manage.py
```

## Live Deployment

MetroClass is deployed on PythonAnywhere for project presentation.

**Live URL:** https://thatmehedi.pythonanywhere.com

---

Created as a university project by [Mehedi Hasan](https://github.com/thatmehedi).
