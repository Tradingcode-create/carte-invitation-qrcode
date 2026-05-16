import hashlib
import hmac
import io
import json
import secrets
import uuid
from decimal import Decimal

import qrcode
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone


class OrganizerProfile(models.Model):
    MARIAGE = "mariage"
    ANNIVERSAIRE = "anniversaire"
    CONCERT = "concert"

    EVENT_CHOICES = [
        (MARIAGE, "Mariage"),
        (ANNIVERSAIRE, "Anniversaire"),
        (CONCERT, "Concert"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="organizer_profile")
    ceremony_type = models.CharField("Type de ceremonie", max_length=20, choices=EVENT_CHOICES)
    planned_invitations = models.PositiveIntegerField("Nombre d'invitations prevu", default=1)
    phone_number = models.CharField("Numero Mobile Money", max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_username()

    def get_event_label(self):
        return dict(self.EVENT_CHOICES).get(self.ceremony_type, self.ceremony_type)

    @property
    def active_subscription(self):
        return self.subscriptions.filter(status=Subscription.STATUS_ACTIVE).order_by("-created_at").first()

    @property
    def has_paid_access(self):
        subscription = self.active_subscription
        return bool(subscription and subscription.is_paid)


class Subscription(models.Model):
    PLAN_STARTER = "starter"
    PLAN_PRO = "pro"
    PLAN_UNLIMITED = "unlimited"

    STATUS_PENDING = "pending"
    STATUS_ACTIVE = "active"
    STATUS_EXPIRED = "expired"
    STATUS_CANCELLED = "cancelled"

    PROVIDER_AIRTEL = "airtel_money"
    PROVIDER_ORANGE = "orange_money"
    PROVIDER_AFRIMONEY = "afrimoney"
    PROVIDER_MPESA = "mpesa"
    PROVIDER_DEMO_CARD = "demo_card"

    PLAN_CHOICES = [
        (PLAN_STARTER, "1 a 199 invitations"),
        (PLAN_PRO, "200 a 599 invitations"),
        (PLAN_UNLIMITED, "Illimite"),
    ]
    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente"),
        (STATUS_ACTIVE, "Actif"),
        (STATUS_EXPIRED, "Expire"),
        (STATUS_CANCELLED, "Annule"),
    ]
    PROVIDER_CHOICES = [
        (PROVIDER_DEMO_CARD, "Carte demo (Visa)"),
        (PROVIDER_AIRTEL, "Airtel Money"),
        (PROVIDER_ORANGE, "Orange Money"),
        (PROVIDER_AFRIMONEY, "AfriMoney"),
        (PROVIDER_MPESA, "M-Pesa"),
    ]

    organizer = models.ForeignKey(
        OrganizerProfile, on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan_code = models.CharField("Plan", max_length=20, choices=PLAN_CHOICES)
    invitation_limit = models.PositiveIntegerField("Quota", null=True, blank=True)
    price_usd = models.DecimalField("Montant USD", max_digits=8, decimal_places=2)
    provider = models.CharField("Operateur Mobile Money", max_length=20, choices=PROVIDER_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.organizer.user.username} - {self.get_plan_code_display()}"

    @classmethod
    def pick_plan(cls, invite_count):
        if invite_count <= 199:
            return cls.PLAN_STARTER, 199, Decimal("79.90")
        if invite_count <= 599:
            return cls.PLAN_PRO, 599, Decimal("239.90")
        return cls.PLAN_UNLIMITED, None, Decimal("999.90")

    @property
    def remaining_invitations(self):
        if self.invitation_limit is None:
            return None
        used = self.organizer.invitations.count()
        return max(self.invitation_limit - used, 0)


class PaymentTransaction(models.Model):
    STATUS_CREATED = "created"
    STATUS_PENDING = "pending"
    STATUS_SUCCEEDED = "succeeded"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_CREATED, "Cree"),
        (STATUS_PENDING, "En attente"),
        (STATUS_SUCCEEDED, "Reussi"),
        (STATUS_FAILED, "Echoue"),
    ]

    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, related_name="payments"
    )
    provider = models.CharField(max_length=20, choices=Subscription.PROVIDER_CHOICES)
    amount_usd = models.DecimalField(max_digits=8, decimal_places=2)
    phone_number = models.CharField(max_length=30)
    transaction_reference = models.CharField(max_length=64, unique=True, editable=False)
    external_reference = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CREATED)
    request_payload = models.TextField(blank=True)
    response_payload = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.transaction_reference

    def save(self, *args, **kwargs):
        if not self.transaction_reference:
            self.transaction_reference = secrets.token_hex(16)
        super().save(*args, **kwargs)

    @staticmethod
    def sign_payload(payload, secret):
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


class SupportMessage(models.Model):
    SENDER_USER = "user"
    SENDER_ADMIN = "admin"
    SENDER_CHOICES = [
        (SENDER_USER, "Utilisateur"),
        (SENDER_ADMIN, "Administration"),
    ]

    organizer = models.ForeignKey(
        OrganizerProfile, on_delete=models.CASCADE, related_name="support_messages"
    )
    sender_type = models.CharField(max_length=10, choices=SENDER_CHOICES, default=SENDER_USER)
    sender_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sent_support_messages"
    )
    subject = models.CharField(max_length=150)
    message = models.TextField()
    is_read_by_user = models.BooleanField(default=False)
    is_read_by_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.organizer.user.username} - {self.subject}"

    def clean(self):
        if self.sender_type == self.SENDER_ADMIN and not (self.sender_user and self.sender_user.is_staff):
            raise ValidationError("Un message admin doit etre envoye par un utilisateur staff.")


class Invitation(models.Model):
    organizer = models.ForeignKey(
        OrganizerProfile, on_delete=models.CASCADE, related_name="invitations"
    )
    subscription = models.ForeignKey(
        Subscription, on_delete=models.PROTECT, related_name="invitations"
    )
    guest_name = models.CharField("Nom de l'invite", max_length=140)
    seat_location = models.CharField("Place dans la salle", max_length=140)
    qr_code = models.ImageField(upload_to="qrcodes/", blank=True)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    share_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    printed_at = models.DateTimeField(null=True, blank=True)
    whatsapp_shared_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.organizer.get_event_label()} - {self.guest_name}"

    @property
    def event_type(self):
        return self.organizer.ceremony_type

    @property
    def event_label(self):
        return self.organizer.get_event_label()

    @property
    def is_locked(self):
        return bool(self.printed_at or self.whatsapp_shared_at)

    def get_payload(self):
        payload = {
            "ceremonie": self.event_label,
            "invite": self.guest_name,
            "place": self.seat_location,
            "organisateur": self.organizer.user.get_full_name() or self.organizer.user.username,
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)

    def _build_slug(self):
        base = slugify(f"{self.organizer.user.username}-{self.guest_name}")[:170] or "invitation"
        candidate = base
        counter = 2
        while Invitation.objects.exclude(pk=self.pk).filter(slug=candidate).exists():
            suffix = f"-{counter}"
            candidate = f"{base[: 180 - len(suffix)]}{suffix}"
            counter += 1
        return candidate

    def _build_qr_code(self):
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(self.get_payload())
        qr.make(fit=True)
        image = qr.make_image(fill_color="#10233f", back_color="white")

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        filename = f"{self.slug or slugify(self.guest_name) or 'invite'}.png"
        return filename, ContentFile(buffer.getvalue())

    def mark_printed(self):
        if not self.printed_at:
            self.printed_at = timezone.now()
            self.save(update_fields=["printed_at", "updated_at"])

    def mark_shared(self):
        if not self.whatsapp_shared_at:
            self.whatsapp_shared_at = timezone.now()
            self.save(update_fields=["whatsapp_shared_at", "updated_at"])

    def save(self, *args, **kwargs):
        self.slug = self.slug or self._build_slug()

        regenerate = False
        if self.pk is None or not self.qr_code:
            regenerate = True
        else:
            previous = (
                Invitation.objects.filter(pk=self.pk)
                .values("guest_name", "seat_location")
                .first()
            )
            current = {
                "guest_name": self.guest_name,
                "seat_location": self.seat_location,
            }
            regenerate = previous != current

        if regenerate:
            filename, qr_content = self._build_qr_code()
            self.qr_code.save(filename, qr_content, save=False)

        super().save(*args, **kwargs)
