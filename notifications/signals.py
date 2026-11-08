from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from courses.models import Announcement
from .models import Notification


@receiver(post_save, sender=Announcement)
def notify_students_on_announcement(sender, instance, created, **kwargs):
    if not created:
        return

    course = instance.course
    enrollments = course.enrollments.select_related('student')
    course_url = reverse('course_detail', args=[course.id])

    notifications_to_create = []
    student_emails = []

    for enrollment in enrollments:
        student = enrollment.student
        notifications_to_create.append(
            Notification(
                recipient=student,
                title=f"New announcement in {course.title}",
                message=f"{instance.title}: {instance.message}",
                notification_type=Notification.ANNOUNCEMENT,
                link=course_url,
            )
        )
        if student.email:
            student_emails.append(student.email)

    # 1. Create in-app notifications in bulk
    Notification.objects.bulk_create(notifications_to_create)

    # 2. Send email notification
    if student_emails:
        send_mail(
            subject=f"[MetroClass] New announcement in {course.title}",
            message=(
                f"Hello,\n\n"
                f"A new announcement was posted in {course.title} by {instance.author.display_name}:\n\n"
                f"Title: {instance.title}\n\n"
                f"{instance.message}\n\n"
                f"Check it on MetroClass."
            ),
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            recipient_list=student_emails,
            fail_silently=True,
        )