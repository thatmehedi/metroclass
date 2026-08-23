from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User

from .models import Assignment, Course, Enrollment, Submission


class DashboardAndEnrollmentTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher", password="safe-password", role="teacher", first_name="Teacher"
        )
        self.student = User.objects.create_user(
            username="student", password="safe-password", role="student", first_name="Student", student_id="S-001"
        )
        self.course = Course.objects.create(teacher=self.teacher, title="Physics")

    def test_student_dashboard_shows_joined_course(self):
        Enrollment.objects.create(course=self.course, student=self.student)
        self.client.force_login(self.student)

        response = self.client.get(reverse("dashboard"))

        self.assertContains(response, "Your Courses")
        self.assertContains(response, "Physics")

    def test_student_cannot_join_archived_course(self):
        self.course.is_archived = True
        self.course.save(update_fields=["is_archived"])
        self.client.force_login(self.student)

        response = self.client.post(reverse("join_course"), {"course_code": self.course.course_code})

        self.assertFormError(response.context["form"], "course_code", "No course was found with this code.")
        self.assertFalse(Enrollment.objects.filter(course=self.course, student=self.student).exists())

    def test_teacher_review_total_excludes_graded_and_archived_work(self):
        active_assignment = Assignment.objects.create(
            course=self.course, created_by=self.teacher, title="Active", instructions="Work", due_date=timezone.now() + timedelta(days=1)
        )
        graded_assignment = Assignment.objects.create(
            course=self.course, created_by=self.teacher, title="Graded", instructions="Work", due_date=timezone.now() + timedelta(days=1)
        )
        archived_course = Course.objects.create(teacher=self.teacher, title="Archived", is_archived=True)
        archived_assignment = Assignment.objects.create(
            course=archived_course, created_by=self.teacher, title="Old", instructions="Work", due_date=timezone.now() + timedelta(days=1)
        )
        Submission.objects.create(assignment=active_assignment, student=self.student, file="submissions/active.txt")
        Submission.objects.create(assignment=graded_assignment, student=self.student, file="submissions/graded.txt", graded_at=timezone.now())
        Submission.objects.create(assignment=archived_assignment, student=self.student, file="submissions/old.txt")
        self.client.force_login(self.teacher)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.context["submission_count"], 1)
        self.assertEqual(list(response.context["recent_submissions"]), [Submission.objects.get(assignment=active_assignment)])
