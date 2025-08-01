from django.test import TestCase, Client
from django.urls import reverse
from .models import Utilisateur, Role, Technicien, Administrateur
#  Création d’un utilisateur via inscrire_utilisateur
class UtilisateurInscriptionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.role_tech = Role.objects.create(nom="TECH", permissions={})
        self.role_admin = Role.objects.create(nom="ADMIN", permissions={})
        self.role_user = Role.objects.create(nom="USER", permissions={})

    def test_creation_utilisateur_tech(self):
        response = self.client.post(reverse('inscrire_utilisateur'), {
            'username': 'tech_user',
            'password': 'pass1234',
            'role': self.role_tech.id,
            'matricule': 'MAT123',
            'telephone': '0600000000',
            'emplacement': 'Bloc A',
            'service': None,
        })
        self.assertEqual(response.status_code, 302)  # redirection
        self.assertTrue(Utilisateur.objects.filter(username='tech_user').exists())
        self.assertTrue(Technicien.objects.filter(utilisateur__username='tech_user').exists())

    def test_creation_utilisateur_admin(self):
        response = self.client.post(reverse('inscrire_utilisateur'), {
            'username': 'admin_user',
            'password': 'pass1234',
            'role': self.role_admin.id,
            'matricule': 'MAT124',
            'telephone': '0700000000',
            'emplacement': 'Direction',
            'service': None,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Administrateur.objects.filter(utilisateur__username='admin_user').exists())


# Réinitialisation mot de passe : demande_changement_mdp + changer_mot_de_passe

from django.contrib.auth import get_user_model

class ConnexionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.role = Role.objects.create(nom="TECH", permissions={})
        self.user = get_user_model().objects.create_user(
            username="tech_user",
            password="pass1234",
            role=self.role,
            matricule="MAT000",
            telephone="0600000000",
            emplacement="Bloc A"
        )

    def test_connexion_valide(self):
        response = self.client.post(reverse('login'), {
            'username': 'tech_user',
            'password': 'pass1234'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('technicien_dashboard'))


#  Formulaires invalides / erreurs
    def test_inscription_utilisateur_existant(self):
        Utilisateur.objects.create_user(
            username='dup_user',
            password='test123',
            role=self.role,
            matricule='MAT777',
            telephone='0666000000',
            emplacement='Bloc B'
        )

        response = self.client.post(reverse('inscrire_utilisateur'), {
            'username': 'dup_user',
            'password': 'test123',
            'role': self.role.id,
            'matricule': 'MAT777',
            'telephone': '0666000000',
            'emplacement': 'Bloc B',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "existe déjà")
