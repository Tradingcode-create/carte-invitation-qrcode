import uuid
from decimal import Decimal

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_profiles_and_subscriptions(apps, schema_editor):
    User = apps.get_model("auth", "User")
    OrganizerProfile = apps.get_model("invitations", "OrganizerProfile")
    Subscription = apps.get_model("invitations", "Subscription")
    Invitation = apps.get_model("invitations", "Invitation")

    for user in User.objects.all():
        profile, _ = OrganizerProfile.objects.get_or_create(
            user_id=user.id,
            defaults={
                "ceremony_type": "mariage",
                "planned_invitations": 1,
                "phone_number": "",
            },
        )
        Subscription.objects.get_or_create(
            organizer_id=profile.id,
            defaults={
                "plan_code": "starter",
                "invitation_limit": 199,
                "price_usd": Decimal("79.90"),
                "provider": "airtel_money",
                "status": "active",
                "is_paid": True,
            },
        )

    orphan_count = Invitation.objects.filter(organizer__isnull=True).count()
    if orphan_count:
        fallback_user, _ = User.objects.get_or_create(
            username="imported_organizer",
            defaults={"email": "imported@example.com"},
        )
        fallback_profile, _ = OrganizerProfile.objects.get_or_create(
            user_id=fallback_user.id,
            defaults={
                "ceremony_type": "mariage",
                "planned_invitations": orphan_count,
                "phone_number": "",
            },
        )
        fallback_subscription, _ = Subscription.objects.get_or_create(
            organizer_id=fallback_profile.id,
            defaults={
                "plan_code": "starter",
                "invitation_limit": 199,
                "price_usd": Decimal("79.90"),
                "provider": "airtel_money",
                "status": "active",
                "is_paid": True,
            },
        )
        Invitation.objects.filter(organizer__isnull=True).update(
            organizer_id=fallback_profile.id,
            subscription_id=fallback_subscription.id,
        )


def populate_share_tokens(apps, schema_editor):
    Invitation = apps.get_model("invitations", "Invitation")
    for invitation in Invitation.objects.all():
        invitation.share_token = uuid.uuid4()
        invitation.save(update_fields=["share_token"])


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("invitations", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrganizerProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("ceremony_type", models.CharField(choices=[("mariage", "Mariage"), ("anniversaire", "Anniversaire"), ("concert", "Concert")], max_length=20, verbose_name="Type de ceremonie")),
                ("planned_invitations", models.PositiveIntegerField(default=1, verbose_name="Nombre d'invitations prevu")),
                ("phone_number", models.CharField(blank=True, max_length=30, verbose_name="Numero Mobile Money")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="organizer_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Subscription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("plan_code", models.CharField(choices=[("starter", "1 a 199 invitations"), ("pro", "200 a 599 invitations"), ("unlimited", "Illimite")], max_length=20, verbose_name="Plan")),
                ("invitation_limit", models.PositiveIntegerField(blank=True, null=True, verbose_name="Quota")),
                ("price_usd", models.DecimalField(decimal_places=2, max_digits=8, verbose_name="Montant USD")),
                ("provider", models.CharField(choices=[("airtel_money", "Airtel Money"), ("orange_money", "Orange Money"), ("afrimoney", "AfriMoney"), ("mpesa", "M-Pesa")], max_length=20, verbose_name="Operateur Mobile Money")),
                ("status", models.CharField(choices=[("pending", "En attente"), ("active", "Actif"), ("expired", "Expire"), ("cancelled", "Annule")], default="pending", max_length=20)),
                ("is_paid", models.BooleanField(default=False)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("organizer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="subscriptions", to="invitations.organizerprofile")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="PaymentTransaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(choices=[("airtel_money", "Airtel Money"), ("orange_money", "Orange Money"), ("afrimoney", "AfriMoney"), ("mpesa", "M-Pesa")], max_length=20)),
                ("amount_usd", models.DecimalField(decimal_places=2, max_digits=8)),
                ("phone_number", models.CharField(max_length=30)),
                ("transaction_reference", models.CharField(editable=False, max_length=64, unique=True)),
                ("external_reference", models.CharField(blank=True, max_length=120)),
                ("status", models.CharField(choices=[("created", "Cree"), ("pending", "En attente"), ("succeeded", "Reussi"), ("failed", "Echoue")], default="created", max_length=20)),
                ("request_payload", models.TextField(blank=True)),
                ("response_payload", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("subscription", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payments", to="invitations.subscription")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddField(
            model_name="invitation",
            name="organizer",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="invitations", to="invitations.organizerprofile"),
        ),
        migrations.AddField(
            model_name="invitation",
            name="printed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="invitation",
            name="share_token",
            field=models.UUIDField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="invitation",
            name="subscription",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="invitations", to="invitations.subscription"),
        ),
        migrations.AddField(
            model_name="invitation",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name="invitation",
            name="whatsapp_shared_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(create_profiles_and_subscriptions, migrations.RunPython.noop),
        migrations.RunPython(populate_share_tokens, migrations.RunPython.noop),
        migrations.RemoveField(model_name="invitation", name="event_title"),
        migrations.RemoveField(model_name="invitation", name="event_type"),
        migrations.RemoveField(model_name="invitation", name="message"),
        migrations.AlterField(
            model_name="invitation",
            name="guest_name",
            field=models.CharField(max_length=140, verbose_name="Nom de l'invite"),
        ),
        migrations.AlterField(
            model_name="invitation",
            name="seat_location",
            field=models.CharField(max_length=140, verbose_name="Place dans la salle"),
        ),
        migrations.AlterField(
            model_name="invitation",
            name="organizer",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="invitations", to="invitations.organizerprofile"),
        ),
        migrations.AlterField(
            model_name="invitation",
            name="subscription",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="invitations", to="invitations.subscription"),
        ),
        migrations.AlterField(
            model_name="invitation",
            name="share_token",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
