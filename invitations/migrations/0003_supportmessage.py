from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("invitations", "0002_accounts_subscriptions_and_locks"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SupportMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sender_type", models.CharField(choices=[("user", "Utilisateur"), ("admin", "Administration")], default="user", max_length=10)),
                ("subject", models.CharField(max_length=150)),
                ("message", models.TextField()),
                ("is_read_by_user", models.BooleanField(default=False)),
                ("is_read_by_admin", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("organizer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="support_messages", to="invitations.organizerprofile")),
                ("sender_user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="sent_support_messages", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
