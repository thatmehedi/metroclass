from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone

from courses.models import Assignment, Submission
from .models import Notification


def send_deadline_reminders():
    now = timezone.now()
    reminder_window = now + timedelta(hours=24)

    # Find assignments due in the next 24 hours that haven't passed yet
    upcoming_assignments = Assignment.objects.filter(
        due_date__gte=now,
        due_date__lte=reminder_window,
    ).select_related('course')

    total_notified = 0

    for assignment in upcoming_assignments:
        course = assignment.course
        enrollments = course.enrollments.select_related('student')
        assignment_url = reverse('assignment_detail', args=[assignment.id])

        for enrollment in enrollments:
            student = enrollment.student

            # Check if student already submitted
            already_submitted = Submission.objects.filter(
                assignment=assignment,
                student=student,
            ).exists()
            if already_submitted:
                continue

            # Avoid sending duplicate reminders
            already_notified = Notification.objects.filter(
                recipient=student,
                notification_type=Notification.DEADLINE,
                link=assignment_url,
            ).exists()
            if already_notified:
                continue

            # 1. Create in-app notification
            Notification.objects.create(
                recipient=student,
                title=f"Reminder: {assignment.title} is due soon!",
                message=(
                    f"Your assignment '{assignment.title}' for {course.title} "
                    f"is due on {assignment.due_date.strftime('%b %d, %Y at %I:%M %p')}."
                ),
                notification_type=Notification.DEADLINE,
                link=assignment_url,
            )

            # 2. Send email
            if student.email:
                send_mail(
                    subject=f"[Reminder] {assignment.title} is due soon",
                    message=(
                        f"Hello {student.display_name},\n\n"
                        f"This is a reminder that '{assignment.title}' in {course.title} "
                        f"is due on {assignment.due_date.strftime('%b %d, %Y at %I:%M %p')}.\n\n"
                        f"Please submit your assignment before the deadline on MetroClass."
                    ),
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                    recipient_list=[student.email],
                    fail_silently=True,
                )

            total_notified += 1

    return total_notified


# Celery periodic task wrapper
try:
    from celery import shared_task

    @shared_task
    def check_deadline_reminders_task():
        return send_deadline_reminders()
except ImportError:
    def check_deadline_reminders_task():
        return send_deadline_reminders()
