# Testing MetroClass

Run the Django system check before deployment:

```bash
python manage.py check
```

Test the main workflow manually:

1. Register or sign in as a teacher.
2. Create a course and copy its course code.
3. Sign in as a student and join the course with that code.
4. Create an assignment as the teacher.
5. Submit the assignment as the student.
6. Grade the submission and add feedback as the teacher.
7. Confirm that the student can view the mark and feedback.
