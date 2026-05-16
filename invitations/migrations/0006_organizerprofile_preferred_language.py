from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invitations", "0005_organizerprofile_last_seen_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="organizerprofile",
            name="preferred_language",
            field=models.CharField(
                choices=[("fr", "Francais"), ("en", "English")],
                default="fr",
                max_length=5,
            ),
        ),
    ]
