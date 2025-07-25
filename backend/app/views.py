from django.shortcuts import render, redirect
from .forms import UtilisateurForm
from .models import Technicien, Administrateur


def inscrire_utilisateur(request):
    if request.method == "POST":
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            utilisateur = form.save(commit=False)
            utilisateur.set_password(
                form.cleaned_data["password"]
            )  # hash le mot de passe
            utilisateur.save()

            # Affecter le rôle
            role = form.cleaned_data["role"]
            if role == "technicien":
                Technicien.objects.create(
                    utilisateur=utilisateur,
                    groupe_affectation="N/A",
                    responsabilites="À définir",
                )

            elif role == "administrateur":
                Administrateur.objects.create(
                    utilisateur=utilisateur, administration="Administration générale"
                )

            return redirect("login")  # redirige vers la page de login
    else:
        form = UtilisateurForm()

    return render(request, "utilisateur/inscription.html", {"form": form})


from django.contrib import messages
from .models import Utilisateur, Role, Technicien, Administrateur


from django.contrib import messages
from .models import Utilisateur, Role, Technicien, Administrateur
from .forms import UtilisateurForm

def inscrire_utilisateur1(request):
    if request.method == "POST":
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]

            # ❌ Vérifier la duplication du username AVANT de créer l'objet
            if Utilisateur.objects.filter(username=username).exists():
                messages.error(request, f"Le nom d'utilisateur '{username}' existe déjà.")
                return render(request, "utilisateur/ajoututilisateur.html", {"form": form})

            # ✅ Sinon on continue
            utilisateur = form.save(commit=False)
            utilisateur.set_password(form.cleaned_data["password"])  # hash du mot de passe

            # Récupérer et associer le rôle
            role_nom = form.cleaned_data["role"]  # ex: 'ADMIN', 'TECH', 'USER'
            try:
                role_obj = Role.objects.get(nom=role_nom)
                utilisateur.role = role_obj
                utilisateur.save()

                # Créer les objets liés selon le rôle
                if role_nom == "TECH":
                    Technicien.objects.create(
                        utilisateur=utilisateur,
                        groupe_affectation="N/A",
                        responsabilites="À définir",
                    )
                elif role_nom == "ADMIN":
                    Administrateur.objects.create(
                        utilisateur=utilisateur,
                        administration="Administration générale",
                    )
                # USER : rien de plus à faire ici

                messages.success(request, "Utilisateur créé avec succès.")
                return redirect("login")

            except Role.DoesNotExist:
                messages.error(request, "Rôle invalide sélectionné.")
        else:
            messages.error(request, "Formulaire invalide.")
    else:
        form = UtilisateurForm()

    return render(request, "utilisateur/ajoututilisateur.html", {"form": form})


from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import *
from django.shortcuts import render, redirect

from .models import Administrateur, Technicien


def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Redirection basée sur le rôle de l'utilisateur
            role = getattr(user.role, "nom", None)  # ADMIN, TECH, USER, etc.

            if role == "ADMIN":
                return redirect("admin_dashboard")
            elif role == "TECH":
                return redirect("technicien_dashboard")
            else:
                return redirect("home")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe invalide.")
    else:
        form = CustomAuthenticationForm()

    return render(request, "utilisateur/login.html", {"form": form})


from django.contrib.auth.decorators import login_required



@login_required
def admin_dashboard(request):
    return render(request, "utilisateur/admin_dashboard.html")


from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def home_view(request):
    return render(request, "utilisateur/home.html")


@login_required
def technicien_dashboard(request):
    return render(request, "utilisateur/technicien_dashboard.html")


from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import (
    TypeEquipementForm,
    EquipementBaseForm,
    EquipementIndividuelForm,
    EquipementDepartementalForm,
    EquipementReseauForm,
)


from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import (
    TypeEquipementForm,
    EquipementBaseForm,
    EquipementIndividuelForm,
    EquipementDepartementalForm,
    EquipementReseauForm,
)
from .models import EquipementIndividuel, EquipementDepartemental, EquipementReseau

def ajouter_equipement(request):
    type_form = TypeEquipementForm(request.POST or None)
    base_form = EquipementBaseForm(request.POST or None)

    type_equipement = (
        request.POST.get("type_equipement") if request.method == "POST" else None
    )

    # Initialisation conditionnelle des formulaires spécifiques
    spec_forms = {
        "INDIVIDUEL": EquipementIndividuelForm(
            request.POST if type_equipement == "INDIVIDUEL" else None
        ),
        "DEPARTEMENTAL": EquipementDepartementalForm(
            request.POST if type_equipement == "DEPARTEMENTAL" else None
        ),
        "RESEAU": EquipementReseauForm(
            request.POST if type_equipement == "RESEAU" else None
        ),
    }

    if request.method == "POST":
        if type_form.is_valid() and base_form.is_valid():
            type_equipement = type_form.cleaned_data["type_equipement"]
            form_specifique = spec_forms.get(type_equipement)

            if form_specifique and form_specifique.is_valid():
                try:
                    equipement = base_form.save(commit=False)
                    equipement.type_equipement = type_equipement
                    equipement.save()

                    sous_equipement = form_specifique.save(commit=False)
                    sous_equipement.equipement = equipement
                    sous_equipement.save()

                    messages.success(request, "L'équipement a été ajouté avec succès!")
                    return redirect("liste_equipements")
                except Exception as e:
                    messages.error(request, f"Erreur lors de l'enregistrement: {str(e)}")
            else:
                messages.error(
                    request,
                    "Erreur dans le formulaire spécifique. Veuillez vérifier les données.",
                )
                print("Erreurs formulaire spécifique:", form_specifique.errors if form_specifique else "Aucun formulaire trouvé")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
            print("Erreurs formulaire base:", base_form.errors)
            print("Erreurs formulaire type:", type_form.errors)

    # ✅ Ajouter ici le formulaire spécifique à afficher
    form_specifique = spec_forms.get(type_equipement)

    return render(
        request,
        "utilisateur/ajoutequip.html",
        {
            "type_form": type_form,
            "base_form": base_form,
            "spec_form": form_specifique,  # ✅ formulaire spécifique pour le template
            "selected_type": type_equipement,
        },
    )


from .models import Equipement


def liste_equipements(request):
    # Récupérer tous les équipements avec leurs relations
    equipements = Equipement.objects.select_related(
        "individuel", "departemental", "reseau"
    ).all()

    return render(
        request, "utilisateur/liste_equipements.html", {"equipements": equipements}
    )


# views.py
from django.contrib.auth.hashers import check_password
from .forms import UtilisateurForm1


def editer_utilisateur(request):
    utilisateur = None
    form = None
    message = ""

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        username = request.POST.get("username_search")

        try:
            utilisateur = Utilisateur.objects.get(id=user_id, username=username)
        except Utilisateur.DoesNotExist:
            message = "Utilisateur introuvable."
            return render(
                request,
                "utilisateur/modifierutilisateur.html",
                {"form": None, "message": message},
            )

        if "modifier" in request.POST:
            form = UtilisateurForm1(request.POST, instance=utilisateur)

            if form.is_valid():
                ancien = form.cleaned_data.get("ancien_mot_de_passe")
                nouveau = form.cleaned_data.get("nouveau_mot_de_passe")

                if ancien and nouveau:
                    if not check_password(ancien, utilisateur.password):
                        message = "Ancien mot de passe incorrect."
                    else:
                        utilisateur = form.save(commit=False)
                        utilisateur.set_password(nouveau)
                        utilisateur.save()
                        message = "Mot de passe modifié avec succès."
                else:
                    form.save()
                    message = "Utilisateur modifié avec succès."
        elif "supprimer" in request.POST:
            utilisateur.delete()
            message = "Utilisateur supprimé avec succès."
            utilisateur = None
            form = None
        else:
            form = UtilisateurForm1(instance=utilisateur)
    else:
        form = None

    return render(
        request,
        "utilisateur/modifierutilisateur.html",
        {
            "form": form,
            "message": message,
        },
    )


def redirection_accueil(request):
    return redirect("login")
