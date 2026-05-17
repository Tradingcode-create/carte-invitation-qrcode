from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invitations", "0006_organizerprofile_preferred_language"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="invitation",
            name="welcome_message",
            field=models.TextField(blank=True, verbose_name="Message de bienvenue"),
        ),
        migrations.CreateModel(
            name="SiteVisit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_key", models.CharField(db_index=True, max_length=80)),
                ("path", models.CharField(max_length=255)),
                ("ip_address", models.CharField(blank=True, max_length=64)),
                ("user_agent", models.CharField(blank=True, max_length=255)),
                ("first_seen_at", models.DateTimeField(auto_now_add=True)),
                ("last_seen_at", models.DateTimeField(auto_now=True)),
                ("hits", models.PositiveIntegerField(default=1)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name="site_visits", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-last_seen_at"],
            },
        ),
    ]
