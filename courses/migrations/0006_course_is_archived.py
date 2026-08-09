from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("courses", "0005_studymaterial_external_link_and_file_optional")]

    operations = [
        migrations.AddField(
            model_name="course",
            name="is_archived",
            field=models.BooleanField(default=False),
        ),
    ]
