from django.core.management.base import BaseCommand
from notifications.tasks import send_deadline_reminders


class Command(BaseCommand):
    help = "Checks upcoming assignment deadlines and notifies students."

    def handle(self, *args, **options):
        self.stdout.write("Checking for approaching deadlines...")
        count = send_deadline_reminders()
        self.stdout.write(self.style.SUCCESS(f"Done! Sent {count} reminders."))