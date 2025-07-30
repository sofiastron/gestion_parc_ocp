from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Utilisateur, Role, Technicien, Administrateur
from .forms import UtilisateurForm

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UtilisateurForm
from .models import Utilisateur, Role, Technicien, Administrateur

def inscrire_utilisateur(request):
    if request.method == "POST":
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            if Utilisateur.objects.filter(username=username).exists():
                messages.error(request, f"Le nom d'utilisateur '{username}' existe déjà.")
                return render(request, "utilisateur/inscription.html", {"form": form})

            utilisateur = form.save(commit=False)
            role_obj = form.cleaned_data["role"]
            utilisateur.role = role_obj
            utilisateur.set_password(form.cleaned_data["password"])
            utilisateur.save()

            # Création des profils liés selon le rôle
            if role_obj.nom == "TECH":
                Technicien.objects.create(
                    utilisateur=utilisateur,
                    groupe_affectation="N/A",
                    responsabilites="À définir"
                )
            elif role_obj.nom == "ADMIN":
                Administrateur.objects.create(
                    utilisateur=utilisateur,
                    administration="Administration générale"
                )
            # Si USER : pas d'objet lié à créer

            messages.success(request, "Inscription réussie ! Vous pouvez maintenant vous connecter.")
            return redirect("login")
        else:
            messages.error(request, "Formulaire invalide.")
    else:
        form = UtilisateurForm()

    return render(request, "utilisateur/inscription.html", {"form": form})

def inscrire_utilisateur1(request):
    if request.method == "POST":
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]

            if Utilisateur.objects.filter(username=username).exists():
                messages.error(request, f"Le nom d'utilisateur '{username}' existe déjà.")
                return render(request, "utilisateur/ajoututilisateur.html", {"form": form})

            utilisateur = form.save(commit=False)
            utilisateur.set_password(form.cleaned_data["password"])  # hash du mot de passe

            role_obj = form.cleaned_data["role"]  # déjà un objet Role
            utilisateur.role = role_obj
            utilisateur.save()

            if role_obj.nom == "TECH":
                Technicien.objects.create(
                    utilisateur=utilisateur,
                    groupe_affectation="N/A",
                    responsabilites="À définir",
                )
            elif role_obj.nom == "ADMIN":
                Administrateur.objects.create(
                    utilisateur=utilisateur,
                    administration="Administration générale",
                )

            messages.success(request, "Utilisateur créé avec succès.")
            return redirect("login")

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


# views.py
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from .forms import DemandeChangementMDPForm
from django.contrib import messages

Utilisateur = get_user_model()

def demande_changement_mdp(request):
    if request.method == "POST":
        form = DemandeChangementMDPForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            matricule = form.cleaned_data['matricule']

            try:
                user = Utilisateur.objects.get(username=username, email=email, matricule=matricule)
                request.session['user_id_reset'] = user.id  # sauvegarder temporairement
                return redirect('changer_mot_de_passe')
            except Utilisateur.DoesNotExist:
                messages.error(request, "Aucun utilisateur ne correspond à ces informations.")
    else:
        form = DemandeChangementMDPForm()

    return render(request, 'utilisateur/demande_changement_mdp.html', {'form': form})

from django.contrib.auth.hashers import make_password

def changer_mot_de_passe(request):
    if 'user_id_reset' not in request.session:
        return redirect('demande_changement_mdp')

    if request.method == 'POST':
        motdepasse = request.POST.get('motdepasse')
        confirmer = request.POST.get('confirmer')

        if motdepasse != confirmer:
            messages.error(request, "Les mots de passe ne correspondent pas.")
        else:
            user = Utilisateur.objects.get(id=request.session['user_id_reset'])
            user.password = make_password(motdepasse)
            user.save()
            del request.session['user_id_reset']
            messages.success(request, "Mot de passe mis à jour avec succès. Vous pouvez maintenant vous connecter.")
            return redirect('login')

    return render(request, 'utilisateur/changer_mot_de_passe.html')


from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def home_view(request):
    return render(request, "utilisateur/home.html")



from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Technicien, Maintenance, Equipement

@login_required
def dashboard_technicien(request):
    utilisateur = request.user

    # Vérifier si utilisateur est un technicien
    try:
        technicien = utilisateur.technicien
    except Technicien.DoesNotExist:
        return HttpResponseForbidden("Accès réservé aux techniciens.")

    # Si POST → le technicien a cliqué sur "valider"
    if request.method == "POST":
        maintenance_id = request.POST.get("maintenance_id")
        maintenance = get_object_or_404(Maintenance, id=maintenance_id, technicien=technicien)

        # Mise à jour de l'état de l'équipement
        equipement = maintenance.equipement
        equipement.etat = "DISPO"
        equipement.save()

        messages.success(request, f"Maintenance pour {equipement.designation} validée, équipement mis à jour comme disponible.")
        return redirect("technicien_dashboard")

    # Récupération des maintenances du technicien
    maintenances = Maintenance.objects.filter(technicien=technicien).order_by('-date')

    return render(request, 'utilisateur/technicien_dashboard.html', {
        'technicien': technicien,
        'maintenances': maintenances,
    })


# @login_required
# def changer_etat(request, tache_id):
#     tache = get_object_or_404(Maintenance, id=tache_id, technicien__utilisateur=request.user)
#     equip = tache.equipement
#     if request.method == 'POST':
#         new_etat = request.POST.get('etat')
#         if new_etat in ['DISPO', 'EN_PANNE', 'MAINTENANCE']:
#             equip.etat = new_etat
#             equip.save(update_fields=['etat'])
#     return redirect('technicien_dashboard')



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


from datetime import date, timedelta
from django.shortcuts import render
from .models import Equipement

def equipements_a_reformer(request):
    # Date limite : aujourd'hui - 5 ans
    limite_reforme = date.today().replace(year=date.today().year - 5)
    # Filtrer les équipements dont date_livraison est avant cette date
    equipements_reformer = Equipement.objects.filter(date_livraison__lt=limite_reforme)

    context = {
        'equipements': equipements_reformer,
        'limite_reforme': limite_reforme,
    }
    return render(request, 'utilisateur/equipements_reformer.html', context)
  


from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Technicien, Equipement, Maintenance

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from app.models import Equipement, Utilisateur, Role, Maintenance  # ajuste le nom du module si besoin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Equipement, Technicien, Maintenance

def reformer_equipement(request, equipement_id):
    equipement = get_object_or_404(Equipement, id=equipement_id)
    techniciens = Technicien.objects.select_related('utilisateur').all()

    if request.method == "POST":
        tech_id = request.POST.get("technicien_id")
        groupe_affectation = request.POST.get("groupe_affectation")
        responsabilites = request.POST.get("responsabilites")
        nouvel_etat = request.POST.get("etat")

        technicien = get_object_or_404(Technicien, id=tech_id)

        # Mise à jour des champs du technicien
        technicien.groupe_affectation = groupe_affectation
        technicien.responsabilites = responsabilites
        technicien.save()

        # Mise à jour de l'état de l'équipement
        if nouvel_etat in dict(Equipement._meta.get_field('etat').choices):
            equipement.etat = nouvel_etat
            equipement.save()
        else:
            messages.error(request, "État invalide sélectionné.")

        # Création d'une maintenance pour trace
        Maintenance.objects.create(
            equipement=equipement,
            technicien=technicien,
            date=timezone.now(),
            description=f"Réforme de l'équipement par {technicien.utilisateur.username}, état changé en {nouvel_etat}"
        )

        messages.success(request, f"{technicien.utilisateur.username} affecté à la réforme. État mis à jour.")
        return redirect('reformer_equipement', equipement_id=equipement.id)

    return render(request, 'utilisateur/reformer.html', {
        'equipement': equipement,
        'techniciens': techniciens,
        'etat_choices': Equipement._meta.get_field('etat').choices,
    })



from .models import Equipement

def equipements_actifs_view(request):
    equipements_actifs = Equipement.objects.filter(etat='DISPO')
    return render(request, 'utilisateur/actifs.html', {'equipements': equipements_actifs})
from django.shortcuts import render
from app.models import Maintenance

def details_interventions_par_service(request):
    maintenances = Maintenance.objects.select_related(
        'technicien__utilisateur',
        'equipement',
        'equipement__departemental__gerant__service',
        'equipement__reseau__service_attribue',
        'equipement__individuel__proprietaire__service',
    ).all()

    data = {}

    for m in maintenances:
        equip = m.equipement
        srv = None

        # Equipement Départemental : service via gerant.service
        if hasattr(equip, 'departemental') and equip.departemental.gerant and equip.departemental.gerant.service:
            srv = equip.departemental.gerant.service

        # Equipement Réseau : service_attribue direct
        elif hasattr(equip, 'reseau') and equip.reseau.service_attribue:
            srv = equip.reseau.service_attribue

        # Equipement Individuel : service via proprietaire.service
        elif hasattr(equip, 'individuel') and equip.individuel.proprietaire and equip.individuel.proprietaire.service:
            srv = equip.individuel.proprietaire.service

        if srv:
            data.setdefault(srv.nom, []).append(m)

    return render(request, 'interventions/details_par_service.html', {
        'interventions_par_service': data
    })


from django.shortcuts import render
from django.db.models import Count
from .models import Maintenance

def interventions_par_technicien(request):
    # Comptage des interventions par technicien
    stats = (
        Maintenance.objects
        .values('technicien__id', 'technicien__utilisateur__username')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Préparer un dict : technicien → total & détails
    data = {}
    for st in stats:
        tech_id = st['technicien__id']
        nom = st['technicien__utilisateur__username']
        data[tech_id] = {'username': nom, 'total': st['total'], 'maintenances': []}

    # Récupérer toutes les maintenances avec relations nécessaires
    maints = Maintenance.objects.select_related(
        'technicien__utilisateur', 'equipement',
        'equipement__departemental__gerant__service',
        'equipement__reseau__service_attribue',
        'equipement__individuel__proprietaire__service',
    )

    for m in maints:
        tech = m.technicien
        if tech and tech.id in data:
            # Trouver le service lié à l'équipement de cette maintenance
            equip = m.equipement
            srv = None

            if hasattr(equip, 'departemental') and equip.departemental.gerant and equip.departemental.gerant.service:
                srv = equip.departemental.gerant.service
            elif hasattr(equip, 'reseau') and equip.reseau.service_attribue:
                srv = equip.reseau.service_attribue
            elif hasattr(equip, 'individuel') and equip.individuel.proprietaire and equip.individuel.proprietaire.service:
                srv = equip.individuel.proprietaire.service

            # Ajouter le service comme attribut dynamique à l'objet maintenance
            m.service = srv

            data[tech.id]['maintenances'].append(m)

    return render(request,
                  'interventions/par_technicien.html',
                  {'data': data})



from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from app.models import Maintenance, Technicien

def interventions_par_equipement(request):
    # Statistiques : nombre d'interventions par équipement
    stats = (
        Maintenance.objects
        .values('equipement__id', 'equipement__designation')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    data = {}
    for st in stats:
        eq_id = st['equipement__id']
        data[eq_id] = {
            'designation': st['equipement__designation'],
            'total': st['total'],
            'maintenances': []
        }

    maints = Maintenance.objects.select_related(
        'equipement', 'technicien__utilisateur'
    )

    for m in maints:
        eq = m.equipement
        if eq.id in data:
            data[eq.id]['maintenances'].append(m)

    techniciens = Technicien.objects.select_related("utilisateur")

    return render(request, 'interventions/par_equipement.html', {
        'data': data,
        'techniciens': techniciens
    })


def assigner_technicien(request, maintenance_id):
    if request.method == 'POST':
        tech_id = request.POST.get('technicien_id')
        maintenance = get_object_or_404(Maintenance, id=maintenance_id)
        maintenance.technicien = get_object_or_404(Technicien, id=tech_id)
        maintenance.save()
    return redirect('interventions_par_technicien')
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, F
from app.models import Maintenance, Equipement

@login_required
def dashboard_admin(request):
    # Statistiques des interventions par service, en incluant tous types d'équipement

    # Queryset pour interventions liées à un équipement départemental (via gerant.service)
    qs_dept = Maintenance.objects.filter(
        equipement__departemental__gerant__service__isnull=False
    ).values(
        service_nom=F('equipement__departemental__gerant__service__nom')
    ).annotate(total=Count('id'))

    # Queryset pour interventions liées à un équipement réseau (via service_attribue)
    qs_reseau = Maintenance.objects.filter(
        equipement__reseau__service_attribue__isnull=False
    ).values(
        service_nom=F('equipement__reseau__service_attribue__nom')
    ).annotate(total=Count('id'))

    # Queryset pour interventions liées à un équipement individuel (via proprietaire.service)
    qs_indiv = Maintenance.objects.filter(
        equipement__individuel__proprietaire__service__isnull=False
    ).values(
        service_nom=F('equipement__individuel__proprietaire__service__nom')
    ).annotate(total=Count('id'))

    # Combiner les résultats par service
    from collections import defaultdict
    service_counts = defaultdict(int)

    for qs in [qs_dept, qs_reseau, qs_indiv]:
        for item in qs:
            service_counts[item['service_nom']] += item['total']

    service_labels = list(service_counts.keys())
    service_data = list(service_counts.values())

    # Statistiques des interventions par technicien
    qs_tech = Maintenance.objects.values('technicien__utilisateur__username').annotate(total=Count('id'))
    tech_labels = [item['technicien__utilisateur__username'] or 'Inconnu' for item in qs_tech]
    tech_data = [item['total'] for item in qs_tech]

    total_maintenances = Maintenance.objects.count()
    total_equipements = Equipement.objects.count()

    return render(request, 'utilisateur/admin_dashboard.html', {
        'service_labels': service_labels,
        'service_data': service_data,
        'tech_labels': tech_labels,
        'tech_data': tech_data,
        'total_maintenances': total_maintenances,
        'total_equipements': total_equipements,
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Equipement, Maintenance, Technicien
from .forms import DemandeInterventionForm
from django.utils import timezone

@login_required
def liste_equipements_individuels(request):
    equips = Equipement.objects.filter(type_equipement='INDIVIDUEL')
    form = DemandeInterventionForm()
    if request.method == 'POST':
        form = DemandeInterventionForm(request.POST)
        if form.is_valid():
            equip = get_object_or_404(Equipement, id=form.cleaned_data['equipement_id'])
            # création d'une nouvelle demande d'intervention :
            Maintenance.objects.create(
                equipement=equip,
                technicien=None,  # assignation ultérieure par admin
                date=timezone.now(),
                description=form.cleaned_data['description']
            )
            equip.etat = 'MAINTENANCE'
            equip.save(update_fields=['etat'])
            return redirect('liste_equipements_individuels')
    return render(request, 'équipements/personnels.html', {
        'equipements': equips,
        'form': form
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import EquipementDepartemental, Maintenance
from .forms import DemandeInterventionForm

@login_required
def liste_equipements_departementaux(request):
    equips = EquipementDepartemental.objects.select_related('equipement').all()
    form = DemandeInterventionForm()
    if request.method == 'POST':
        form = DemandeInterventionForm(request.POST)
        if form.is_valid():
            equip = get_object_or_404(EquipementDepartemental, equipement__id=form.cleaned_data['equipement_id']).equipement
            Maintenance.objects.create(
                equipement=equip,
                technicien=None,
                date=timezone.now(),
                description=form.cleaned_data['description']
            )
            equip.etat = 'MAINTENANCE'
            equip.save(update_fields=['etat'])
            return redirect('liste_equipements_departementaux')
    return render(request, 'équipements/departementaux.html', {
        'equipements': equips,
        'form': form
    })


@login_required
def liste_equipements_reseau(request):
    equips = Equipement.objects.filter(type_equipement='RESEAU')
    form = DemandeInterventionForm()
    if request.method == 'POST':
        form = DemandeInterventionForm(request.POST)
        if form.is_valid():
            equip = get_object_or_404(Equipement, id=form.cleaned_data['equipement_id'])
            Maintenance.objects.create(
                equipement=equip,
                technicien=None,
                date=timezone.now(),
                description=form.cleaned_data['description']
            )
            equip.etat = 'MAINTENANCE'
            equip.save(update_fields=['etat'])
            return redirect('liste_equipements_reseau')
    return render(request, 'équipements/réseaux.html', {
        'equipements': equips,
        'form': form
    })
