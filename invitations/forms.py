from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .localization import tr_text
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
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "+243..."}),
    )
    provider = forms.ChoiceField(
        label="Operateur de paiement",
        choices=Subscription.PROVIDER_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    preferred_language = forms.ChoiceField(
        label="Langue preferee",
        choices=OrganizerProfile.LANGUAGE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        initial=OrganizerProfile.LANG_FR,
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
            "preferred_language",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]:
            self.fields[name].widget.attrs["class"] = "form-control"

        self.fields["username"].label = tr_text("Nom d'utilisateur", "Username")
        self.fields["first_name"].label = tr_text("Prenom", "First name")
        self.fields["last_name"].label = tr_text("Nom", "Last name")
        self.fields["email"].label = "Email"
        self.fields["ceremony_type"].label = tr_text("Type de ceremonie", "Ceremony type")
        self.fields["planned_invitations"].label = tr_text(
            "Nombre d'invitations souhaite", "Desired number of invitations"
        )
        self.fields["phone_number"].label = tr_text("Numero Mobile Money", "Mobile Money number")
        self.fields["provider"].label = tr_text("Operateur de paiement", "Payment provider")
        self.fields["preferred_language"].label = tr_text("Langue preferee", "Preferred language")
        self.fields["password1"].label = tr_text("Mot de passe", "Password")
        self.fields["password2"].label = tr_text("Confirmation du mot de passe", "Confirm password")

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
        fields = ["guest_name", "seat_location", "welcome_message"]
        widgets = {
            "guest_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex. Couple Kasongo"}
            ),
            "seat_location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Table 8, rangee B"}
            ),
            "welcome_message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Nous sommes heureux de vous accueillir a cette celebration.",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["guest_name"].label = tr_text("Nom de l'invite ou du couple", "Guest or couple name")
        self.fields["guest_name"].widget.attrs["placeholder"] = tr_text(
            "Ex. Couple Kasongo", "E.g. Kasongo Couple"
        )
        self.fields["seat_location"].label = tr_text("Place dans la salle", "Seat location")
        self.fields["seat_location"].widget.attrs["placeholder"] = tr_text(
            "Table 8, rangee B", "Table 8, row B"
        )
        self.fields["welcome_message"].label = tr_text("Message de bienvenue", "Welcome message")
        self.fields["welcome_message"].required = False
        self.fields["welcome_message"].widget.attrs["placeholder"] = tr_text(
            "Nous sommes heureux de vous accueillir a cette celebration.",
            "We are delighted to welcome you to this celebration.",
        )


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
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "+243..."}),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["planned_invitations"].label = tr_text(
            "Nombre d'invitations pour le nouvel abonnement",
            "Number of invitations for the new subscription",
        )
        self.fields["phone_number"].label = tr_text("Numero Mobile Money", "Mobile Money number")
        self.fields["provider"].label = tr_text("Operateur", "Provider")
        self.fields["cardholder_name"].label = tr_text("Nom sur la carte", "Name on card")
        self.fields["card_number"].label = tr_text("Numero de carte", "Card number")
        self.fields["expiry_date"].label = tr_text("Expiration", "Expiry")

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
                    tr_text(
                        "Pour le mode carte demo, renseignez le nom, le numero, l'expiration et le CVV.",
                        "For demo card mode, fill in the name, number, expiry date, and CVV.",
                    )
                )
            if card_number not in {"4111111111111111", "4242424242424242"}:
                raise forms.ValidationError(
                    tr_text(
                        "Utilisez une carte de test: 4111 1111 1111 1111 ou 4242 4242 4242 4242.",
                        "Use a test card: 4111 1111 1111 1111 or 4242 4242 4242 4242.",
                    )
                )
        elif not phone_number:
            self.add_error(
                "phone_number",
                tr_text("Le numero Mobile Money est obligatoire.", "Mobile Money number is required."),
            )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subject"].label = tr_text("Sujet", "Subject")
        self.fields["subject"].widget.attrs["placeholder"] = tr_text(
            "Besoin d'aide sur mon abonnement", "Need help with my subscription"
        )
        self.fields["message"].label = tr_text("Message", "Message")
        self.fields["message"].widget.attrs["placeholder"] = tr_text(
            "Expliquez votre demande ici.", "Explain your request here."
        )


class ContactAdminReplyForm(forms.Form):
    message = forms.CharField(
        label="Votre reponse",
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 5, "placeholder": "Ecrivez votre reponse ici."}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["message"].label = tr_text("Votre reponse", "Your reply")
        self.fields["message"].widget.attrs["placeholder"] = tr_text(
            "Ecrivez votre reponse ici.", "Write your reply here."
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subject"].label = tr_text("Sujet", "Subject")
        self.fields["subject"].widget.attrs["placeholder"] = tr_text(
            "Reponse a votre demande", "Reply to your request"
        )
        self.fields["message"].label = tr_text("Reponse", "Reply")
        self.fields["message"].widget.attrs["placeholder"] = tr_text(
            "Message de l'administration", "Administration message"
        )


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label="Fichier Excel",
        help_text="Format .xlsx avec deux colonnes: nom de l'invite ou du couple, puis emplacement.",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["excel_file"].label = tr_text("Fichier Excel", "Excel file")
        self.fields["excel_file"].help_text = tr_text(
            "Format .xlsx avec deux colonnes: nom de l'invite ou du couple, puis emplacement.",
            ".xlsx format with two columns: guest or couple name, then seat location.",
        )


class StyledAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = tr_text("Nom d'utilisateur", "Username")
        self.fields["password"].label = tr_text("Mot de passe", "Password")
