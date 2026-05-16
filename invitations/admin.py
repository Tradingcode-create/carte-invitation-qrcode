from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User

from .models import Invitation, OrganizerProfile, PaymentTransaction, Subscription, SupportMessage


@admin.register(OrganizerProfile)
class OrganizerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "ceremony_type", "planned_invitations", "phone_number", "created_at")
    list_filter = ("ceremony_type", "created_at")
    search_fields = ("user__username", "user__email", "phone_number")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "organizer",
        "plan_code",
        "invitation_limit",
        "price_usd",
        "provider",
        "status",
        "is_paid",
        "paid_at",
    )
    list_filter = ("plan_code", "provider", "status", "is_paid")
    search_fields = ("organizer__user__username", "organizer__user__email")


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_reference",
        "subscription",
        "provider",
        "amount_usd",
        "phone_number",
        "status",
        "created_at",
    )
    list_filter = ("provider", "status", "created_at")
    search_fields = ("transaction_reference", "external_reference", "subscription__organizer__user__username")


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = (
        "guest_name",
        "organizer",
        "seat_location",
        "printed_at",
        "whatsapp_shared_at",
        "created_at",
    )
    list_filter = ("organizer__ceremony_type", "printed_at", "whatsapp_shared_at")
    search_fields = ("guest_name", "organizer__user__username", "seat_location")
    readonly_fields = ("share_token",)


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "organizer", "sender_type", "is_read_by_admin", "is_read_by_user", "created_at")
    list_filter = ("sender_type", "is_read_by_admin", "is_read_by_user", "created_at")
    search_fields = ("subject", "message", "organizer__user__username", "organizer__user__email")
    autocomplete_fields = ("organizer", "sender_user")


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_active")
