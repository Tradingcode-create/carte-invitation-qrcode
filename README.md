# App QR Mariage

Application Django pour creer des invitations avec QR code, comptes utilisateurs, abonnements et paiement Mobile Money.

## Ce qui a ete ajoute

- inscription et connexion utilisateur
- profil organisateur avec type de ceremonie et volume d'invitations
- abonnement automatique selon 3 categories:
  - 1 a 199 invitations: 79.90 USD
  - 200 a 599 invitations: 239.90 USD
  - illimite: 999.90 USD
- paiement prepare pour Airtel Money, Orange Money, AfriMoney et M-Pesa
- paiement local de demonstration par carte Visa de test
- invitations basees uniquement sur:
  - nom de l'invite
  - place dans la salle
- QR code telechargeable seulement si l'abonnement est paye
- image d'invitation SVG telechargeable pour partage externe
- image d'invitation JPEG telechargeable
- partage WhatsApp
- impression avec verrouillage automatique
- modification et suppression interdites apres impression ou partage
- suivi admin des utilisateurs, abonnements et transactions
- import Excel des invites avec generation automatique des invitations
- export Excel du rapport admin

## Installation

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Variables d'environnement pour les APIs de paiement

Configurez selon le fournisseur choisi:

```bash
AIRTEL_MONEY_API_URL=
AIRTEL_MONEY_API_KEY=
AIRTEL_MONEY_API_SECRET=

ORANGE_MONEY_API_URL=
ORANGE_MONEY_API_KEY=
ORANGE_MONEY_API_SECRET=

AFRIMONEY_API_URL=
AFRIMONEY_API_KEY=
AFRIMONEY_API_SECRET=

MPESA_API_URL=
MPESA_API_KEY=
MPESA_API_SECRET=
```

Le projet prepare:

- la creation de transaction
- la signature HMAC des charges utiles
- un endpoint de callback pour confirmer un paiement

## Mode demo local

Pour tester sans API externe:

- choisissez `Carte demo (Visa)` sur l'ecran abonnement
- utilisez `4111 1111 1111 1111` ou `4242 4242 4242 4242`
- entrez n'importe quelle date d'expiration valide visuellement
- entrez n'importe quel CVV

Le paiement sera valide localement et activera l'abonnement.

Le branchement HTTP reel vers chaque fournisseur reste a finaliser avec vos identifiants marchands et leur documentation de production.

## URLs utiles

- `/` : accueil
- `/inscription/` : creation de compte
- `/accounts/login/` : connexion
- `/abonnement/` : paiement et abonnement
- `/invites/` : liste des invites
- `/nouvelle/` : nouvelle invitation
- `/admin/` : administration Django
