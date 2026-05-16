from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Invitation, OrganizerProfile, Subscription


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label="Prenom", max_length=150)
    last_name = forms.CharField(label="Nom", max_length=150)
    email = forms.EmailField()
    ceremony_type = forms.ChoiceField(
        label="Type de ceremonie",
        choices=OrganizerProfile.EVENT_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    planned_invitations = forms.IntegerField(
        label="Nombre d'invitations souhaite",
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "120"}),
    )
    phone_number = forms.CharField(
        label="Numero Mobile Money",
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "+243..."})
    )
    provider = forms.ChoiceField(
        label="Operateur de paiement",
        choices=Subscription.PROVIDER_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "ceremony_type",
            "planned_invitations",
            "phone_number",
            "provider",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ["username", "first_name", "last_name", "email", "password1", "password2"]:
            self.fields[name].widget.attrs["class"] = "form-control"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class InvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ["guest_name", "seat_location"]
        widgets = {
            "guest_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex. Couple Kasongo"}
            ),
            "seat_location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Table 8, rangee B"}
            ),
        }


class PaymentInitiationForm(forms.Form):
    planned_invitations = forms.IntegerField(
        label="Nombre d'invitations pour le nouvel abonnement",
        min_value=1,
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "120"}),
    )
    phone_number = forms.CharField(
        label="Numero Mobile Money",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "+243..."})
    )
    provider = forms.ChoiceField(
        label="Operateur",
        choices=Subscription.PROVIDER_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    cardholder_name = forms.CharField(
        label="Nom sur la carte",
        max_length=120,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Jean Kasongo"}),
    )
    card_number = forms.CharField(
        label="Numero de carte",
        max_length=19,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "4111 1111 1111 1111"}),
    )
    expiry_date = forms.CharField(
        label="Expiration",
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "12/30"}),
    )
    cvv = forms.CharField(
        label="CVV",
        max_length=4,
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "123"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        provider = cleaned_data.get("provider")
        phone_number = (cleaned_data.get("phone_number") or "").strip()
        card_number = (cleaned_data.get("card_number") or "").replace(" ", "")
        expiry_date = (cleaned_data.get("expiry_date") or "").strip()
        cvv = (cleaned_data.get("cvv") or "").strip()
        cardholder_name = (cleaned_data.get("cardholder_name") or "").strip()

        if provider == Subscription.PROVIDER_DEMO_CARD:
            if not all([cardholder_name, card_number, expiry_date, cvv]):
                raise forms.ValidationError(
                    "Pour le mode carte demo, renseignez le nom, le numero, l'expiration et le CVV."
                )
            if card_number not in {"4111111111111111", "4242424242424242"}:
                raise forms.ValidationError(
                    "Utilisez une carte de test: 4111 1111 1111 1111 ou 4242 4242 4242 4242."
                )
        else:
            if not phone_number:
                self.add_error("phone_number", "Le numero Mobile Money est obligatoire.")

        return cleaned_data


class ContactAdminForm(forms.Form):
    subject = forms.CharField(
        label="Sujet",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Besoin d'aide sur mon abonnement"}),
    )
    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 6, "placeholder": "Expliquez votre demande ici."}
        ),
    )


class AdminSupportReplyForm(forms.Form):
    subject = forms.CharField(
        label="Sujet",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Reponse a votre demande"}),
    )
    message = forms.CharField(
        label="Reponse",
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 5, "placeholder": "Message de l'administration"}
        ),
    )


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label="Fichier Excel",
        help_text="Format .xlsx avec deux colonnes: nom de l'invite ou du couple, puis emplacement.",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx"}),
    )


class StyledAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
