import random
import string

from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


def generate_course_code():
    characters = string.ascii_uppercase + string.digits

    while True:
        code = "".join(random.choices(characters, k=6))

        if not Course.objects.filter(course_code=code).exists():
            return code


class CourseGroup(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_groups",
        limit_choices_to={"role": "teacher"},
    )
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "name"], name="unique_teacher_course_group"
            )
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.teacher.display_name} — {self.name}"


class Course(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_courses",
        limit_choices_to={"role": "teacher"},
    )
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    group = models.ForeignKey(
        CourseGroup,
        on_delete=models.SET_NULL,
        related_name="courses",
        null=True,
        blank=True,
    )
    course_code = models.CharField(
        max_length=6,
        unique=True,
        default=generate_course_code,
        editable=False,
    )
    accent_color = models.CharField(
        max_length=7,
        default="#2F6F83",
        validators=[
            RegexValidator(
                regex=r"^#[0-9A-Fa-f]{6}$",
                message="Choose a valid six-digit color.",
            )
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
        limit_choices_to={"role": "student"},
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "student"],
                name="unique_course_enrollment",
            )
        ]

    def __str__(self):
        return f"{self.student.display_name} - {self.course.title}"


class Announcement(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="announcements",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="announcements",
        limit_choices_to={"role": "teacher"},
    )
    title = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class StudyMaterial(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="study_materials",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_materials",
        limit_choices_to={"role": "teacher"},
    )
    title = models.CharField(max_length=150)
    file = models.FileField(upload_to="study_materials/", blank=True, null=True)
    external_link = models.URLField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title


class Assignment(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_assignments",
        limit_choices_to={"role": "teacher"},
    )
    title = models.CharField(max_length=150)
    instructions = models.TextField()
    resource_file = models.FileField(
        upload_to="assignment_resources/", blank=True, null=True
    )
    resource_link = models.URLField(blank=True)
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_date"]

    def __str__(self):
        return self.title


class Submission(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submissions",
        limit_choices_to={"role": "student"},
    )
    file = models.FileField(upload_to="submissions/")
    comment = models.TextField(blank=True)
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["assignment", "student"],
                name="unique_assignment_submission",
            )
        ]
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.student.display_name} - {self.assignment.title}"
