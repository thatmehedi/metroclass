from django.core.validators import RegexValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0008_submission_feedback_submission_graded_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="accent_color",
            field=models.CharField(
                default="#2F6F83",
                max_length=7,
                validators=[
                    RegexValidator(
                        message="Choose a valid six-digit color.",
                        regex="^#[0-9A-Fa-f]{6}$",
                    )
                ],
            ),
        ),
    ]
