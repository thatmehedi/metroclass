from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    STUDENT = "student"
    TEACHER = "teacher"

    ROLE_CHOICES = [
        (STUDENT, "Student"),
        (TEACHER, "Teacher"),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
    )
    student_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Student ID / Roll Number",
    )

    @property
    def display_name(self):
        return self.get_full_name().strip() or self.username
