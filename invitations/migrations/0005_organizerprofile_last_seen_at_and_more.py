from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("invitations", "0004_alter_invitation_updated_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="organizerprofile",
            name="last_seen_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="organizerprofile",
            name="support_thread_subject",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name="organizerprofile",
            name="support_user_can_send",
            field=models.BooleanField(default=True),
        ),
    ]
