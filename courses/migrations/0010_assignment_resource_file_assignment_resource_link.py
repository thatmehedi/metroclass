from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0009_course_accent_color"),
    ]

    operations = [
        migrations.AddField(
            model_name="assignment",
            name="resource_file",
            field=models.FileField(blank=True, null=True, upload_to="assignment_resources/"),
        ),
        migrations.AddField(
            model_name="assignment",
            name="resource_link",
            field=models.URLField(blank=True),
        ),
    ]
