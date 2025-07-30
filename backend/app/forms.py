from django import forms
from .models import Utilisateur, Service
from django.contrib.auth.forms import AuthenticationForm
from .models import Utilisateur, Role
from django import forms
from .models import Utilisateur, Role, Service

class UtilisateurForm(forms.ModelForm):
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        label='Rôle',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        label='Service',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Utilisateur
        fields = ['username', 'password', 'matricule', 'telephone', 'emplacement', 'service', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'emplacement': forms.TextInput(attrs={'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-select'}),
        }

from django.contrib.auth.forms import AuthenticationForm
from django import forms

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom d'utilisateur"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'})
    )

from django import forms
from .models import Equipement, EquipementIndividuel, EquipementDepartemental, EquipementReseau
from django.core.validators import validate_ipv4_address
from django.core.exceptions import ValidationError

def validate_date_not_future(value):
    from django.utils import timezone
    if value > timezone.now().date():
        raise ValidationError("La date ne peut pas être dans le futur")

class TypeEquipementForm(forms.Form):
    type_equipement = forms.ChoiceField(
        choices=Equipement.TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Type d'équipement",
        required=True
    )

class EquipementBaseForm(forms.ModelForm):
    date_livraison = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        validators=[validate_date_not_future],
        input_formats=['%Y-%m-%d']
    )
    
    class Meta:
        model = Equipement
        fields = ['designation', 'fabriquant', 'modele', 'etat', 'destination', 
                 'localisation', 'date_livraison', 'duree_garantie', 'ip']
        widgets = {
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'fabriquant': forms.TextInput(attrs={'class': 'form-control'}),
            'modele': forms.TextInput(attrs={'class': 'form-control'}),
            'etat': forms.Select(attrs={'class': 'form-select'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'localisation': forms.TextInput(attrs={'class': 'form-control'}),
            'duree_garantie': forms.NumberInput(attrs={'class': 'form-control'}),
            'ip': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '192.168.1.1'
            }),
        }
        labels = {
            'ip': 'Adresse IP (optionnelle)'
        }

class EquipementIndividuelForm(forms.ModelForm):
    date_affectation = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d']
    )
    date_mise_en_service = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d']
    )

    class Meta:
        model = EquipementIndividuel
        fields = ['type', 'date_affectation', 'date_mise_en_service', 'proprietaire']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'proprietaire': forms.Select(attrs={'class': 'form-select'}),
        }

class EquipementDepartementalForm(forms.ModelForm):
    date_affectation = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d']
    )
    date_mise_en_service = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d']
    )

    class Meta:
        model = EquipementDepartemental
        fields = ['type', 'date_affectation', 'date_mise_en_service', 'emplacement', 
                 'gerant', 'service_attribue']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'emplacement': forms.TextInput(attrs={'class': 'form-control'}),
            'gerant': forms.Select(attrs={'class': 'form-select'}),
            'service_attribue': forms.Select(attrs={'class': 'form-select'}),
        }

class EquipementReseauForm(forms.ModelForm):
    class Meta:
        model = EquipementReseau
        fields = ['type', 'adresse_mac', 'service_attribue']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'adresse_mac': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': '^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
                'title': 'Format: 00:1A:2B:3C:4D:5E'
            }),
            'service_attribue': forms.Select(attrs={'class': 'form-select'}),
        }
from django import forms
from .models import Utilisateur

class UtilisateurForm1(forms.ModelForm):
    ancien_mot_de_passe = forms.CharField(label="Ancien mot de passe", widget=forms.PasswordInput, required=False)
    nouveau_mot_de_passe = forms.CharField(label="Nouveau mot de passe", widget=forms.PasswordInput, required=False)
    confirmer_mot_de_passe = forms.CharField(label="Confirmer le nouveau mot de passe", widget=forms.PasswordInput, required=False)

    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'role']

    def clean(self):
        cleaned_data = super().clean()
        ancien = cleaned_data.get('ancien_mot_de_passe')
        nouveau = cleaned_data.get('nouveau_mot_de_passe')
        confirmer = cleaned_data.get('confirmer_mot_de_passe')

        if nouveau:
            if not ancien:
                raise forms.ValidationError("Veuillez entrer l’ancien mot de passe.")
            if nouveau != confirmer:
                raise forms.ValidationError("Les nouveaux mots de passe ne correspondent pas.")



from django import forms

class DemandeInterventionForm(forms.Form):
    equipement_id = forms.IntegerField(widget=forms.HiddenInput)
    description = forms.CharField(
        label="Description de la panne ou du problème",
        widget=forms.Textarea(attrs={'rows':3}),
        max_length=500
    )



# forms.py
from django import forms

class DemandeChangementMDPForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur")
    matricule = forms.CharField(label="Matricule")
    email = forms.EmailField(label="Email")