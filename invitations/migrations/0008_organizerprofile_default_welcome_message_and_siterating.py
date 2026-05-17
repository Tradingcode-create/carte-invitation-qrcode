from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invitations", "0007_sitevisit_invitation_welcome_message"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="organizerprofile",
            name="default_welcome_message",
            field=models.TextField(blank=True),
        ),
        migrations.CreateModel(
            name="SiteRating",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("stars", models.PositiveSmallIntegerField(default=5)),
                ("comment", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organizer", models.OneToOneField(on_delete=models.deletion.CASCADE, related_name="site_rating", to="invitations.organizerprofile")),
            ],
            options={"ordering": ["-updated_at"]},
        ),
    ]
