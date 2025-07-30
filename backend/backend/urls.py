"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app.views import inscrire_utilisateur,login_view
from django.contrib.auth.views import LogoutView

from django.contrib.auth import views as auth_views
from app.forms import CustomAuthenticationForm  
from app import views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('inscription/', inscrire_utilisateur, name='inscription'),
    
    path('', views.redirection_accueil), 
    
    path('dashboard/admin/', views.dashboard_admin, name='admin_dashboard'),
    path('home/', views.home_view, name='home'),
    path('dashboard/technicien/', views.dashboard_technicien, name='technicien_dashboard'),
    # path('dashboard/technicien/taches/changer_etat/<int:tache_id>/', views.changer_etat, name='changer_etat'),

    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/admin/ajouter-equipement/', views.ajouter_equipement, name='ajouter_equipement'),
    path('equipements/', views.liste_equipements, name='liste_equipements'),
    path('dashboard/admin/editer/', views.editer_utilisateur, name='editer_utilisateur'),
    path('dashboard/admin/ajoututilisateur/', views.inscrire_utilisateur1, name='ajouter-utilisateur'),
    path('login/', login_view, name='login'),

    path('demande-mdp/', views.demande_changement_mdp, name='demande_changement_mdp'),
    path('changer-mdp/', views.changer_mot_de_passe, name='changer_mot_de_passe'),


    path('equipements/reformer/', views.equipements_a_reformer, name='equipements_reformer'),
    path('equipement/<int:equipement_id>/reformer/', views.reformer_equipement, name='reformer_equipement'),
    path('dashboard/admin/equipements/actifs/', views.equipements_actifs_view, name='equipements_actifs'),
    path('dashboard/admin/interventions/service/details/', 
         views.details_interventions_par_service, 
         name='interventions_details_par_service'),
    path('dashboard/admin/interventions/technicien/', views.interventions_par_technicien, name='interventions_par_technicien'),
    
    path('dashboard/admin/interventions/equipement/', views.interventions_par_equipement, name='interventions_par_equipement'),
    path('dashboard/admin/interventions/assigner/<int:maintenance_id>/', views.assigner_technicien, name='assigner_technicien'),

    
    path('home/equipements/individuels/', views.liste_equipements_individuels, name='liste_equipements_individuels'),

    path('home/equipements/departementaux/', views.liste_equipements_departementaux, name='liste_equipements_departementaux'),
 
    path('home/equipements/reseau/', views.liste_equipements_reseau, name='liste_equipements_reseau'),


]

