from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Invitation, OrganizerProfile, Subscription


class SubscriptionModelTests(TestCase):
    def test_pick_plan_starter(self):
        plan_code, limit, price = Subscription.pick_plan(150)
        self.assertEqual(plan_code, Subscription.PLAN_STARTER)
        self.assertEqual(limit, 199)
        self.assertEqual(price, Decimal("79.90"))


class InvitationLockTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="organizer", password="pass12345")
        self.profile = OrganizerProfile.objects.create(
            user=self.user,
            ceremony_type=OrganizerProfile.MARIAGE,
            planned_invitations=20,
            phone_number="+243900000001",
        )
        self.subscription = Subscription.objects.create(
            organizer=self.profile,
            plan_code=Subscription.PLAN_STARTER,
            invitation_limit=199,
            price_usd=Decimal("79.90"),
            provider=Subscription.PROVIDER_AIRTEL,
            status=Subscription.STATUS_ACTIVE,
            is_paid=True,
        )
        self.invitation = Invitation.objects.create(
            organizer=self.profile,
            subscription=self.subscription,
            guest_name="Aimee et Claude",
            seat_location="Table 4",
        )

    def test_cannot_delete_after_print(self):
        self.client.login(username="organizer", password="pass12345")
        self.invitation.mark_printed()
        response = self.client.post(reverse("invitations:delete", args=[self.invitation.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Invitation.objects.filter(pk=self.invitation.pk).exists())

    def test_download_qrcode_requires_paid_subscription(self):
        self.client.login(username="organizer", password="pass12345")
        response = self.client.get(reverse("invitations:download-qrcode", args=[self.invitation.slug]))
        self.assertEqual(response.status_code, 200)
