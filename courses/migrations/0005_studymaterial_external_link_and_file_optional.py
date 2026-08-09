# Generated manually for MetroClass lecture links and optional uploaded files.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0004_assignment_studymaterial_submission"),
    ]

    operations = [
        migrations.AlterField(
            model_name="studymaterial",
            name="file",
            field=models.FileField(blank=True, null=True, upload_to="study_materials/"),
        ),
        migrations.AddField(
            model_name="studymaterial",
            name="external_link",
            field=models.URLField(blank=True),
        ),
    ]
