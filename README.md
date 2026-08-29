# MetroClass

MetroClass is a role-based **Classroom Management System** built with Django for a university project. It helps teachers manage course activities and lets students follow their academic work from one place.

## Live Demo

**Website:** [https://thatmehedi.pythonanywhere.com/](https://thatmehedi.pythonanywhere.com/)

| Role | Username | Password |
| --- | --- | --- |
| Student | `s1` | `Demo@12345` |
| Teacher | `t1` | `Demo@12345` |

## Main Features

### Student

- Register, sign in, sign out, edit profile, and change password
- Join courses using a course code
- View joined courses, announcements, lectures, and assignments
- Submit, update, or delete assignment submissions
- View deadlines, marks, and teacher feedback
- Leave courses and view archived courses

### Teacher

- Create, edit, archive, and delete courses
- Create groups for courses such as batch or section
- Post, edit, and delete announcements
- Upload lecture files and add external learning links
- Create and edit assignments with due dates and resources
- View student submissions and provide marks with written feedback
- Review pending submissions from the teacher dashboard

## Technology Stack

- Python
- Django
- SQLite
- HTML
- CSS
- JavaScript
- Bootstrap 5
- GitHub
- PythonAnywhere

## Project Structure

```text
MetroClass/
├── accounts/      # Authentication, users, profiles, dashboards
├── courses/       # Courses, announcements, lectures, assignments, submissions
├── core/          # Home page, shared templates, CSS, logo and static files
├── metroclass/    # Django settings and root URL configuration
├── manage.py       # Django command-line management file
└── requirements.txt
```

## Run Locally

```bash
git clone https://github.com/thatmehedi/metroclass.git
cd metroclass
python -m venv venv
```

Activate the virtual environment.

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies and start the project:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in a browser.

## Deployment

The project is deployed on PythonAnywhere for online demonstration.

**Live URL:** [https://thatmehedi.pythonanywhere.com/](https://thatmehedi.pythonanywhere.com/)

---

Created by [Mehedi Hasan](https://github.com/thatmehedi) as a university project.
