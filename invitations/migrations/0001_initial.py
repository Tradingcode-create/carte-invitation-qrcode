from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Invitation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_type", models.CharField(choices=[("mariage", "Mariage"), ("anniversaire", "Anniversaire"), ("concert", "Concert")], max_length=20, verbose_name="Type d'evenement")),
                ("event_title", models.CharField(max_length=140, verbose_name="Nom de l'evenement")),
                ("guest_name", models.CharField(max_length=140, verbose_name="Nom de l'invite")),
                ("seat_location", models.CharField(max_length=140, verbose_name="Emplacement")),
                ("message", models.TextField(blank=True, verbose_name="Message personnalise")),
                ("qr_code", models.ImageField(blank=True, upload_to="qrcodes/")),
                ("slug", models.SlugField(blank=True, max_length=180, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
