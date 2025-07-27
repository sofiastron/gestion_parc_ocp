from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


# -----------------------------
# SERVICE
# -----------------------------
class Service(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom
    
# -----------------------------
# ROLE
# -----------------------------
class Role(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrateur'),
        ('TECH', 'Technicien'),
        ('USER', 'Utilisateur'),
    )
    nom = models.CharField(max_length=10, choices=ROLE_CHOICES)
    permissions = models.JSONField()

    def __str__(self):
        return self.nom


# -----------------------------
# UTILISATEUR
# -----------------------------
class Utilisateur(AbstractUser):

    # email = models.EmailField(unique=True)/

    
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    matricule = models.CharField(max_length=50, unique=True)
    telephone = models.CharField(max_length=20)
    emplacement = models.CharField(max_length=100)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, related_name='utilisateurs')

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # ✓ corriger le conflit avec auth.User
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',  # ✓ corriger le conflit avec auth.User
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username


# -----------------------------
# TECHNICIEN
# -----------------------------
class Technicien(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='technicien')
    groupe_affectation = models.CharField(max_length=100)
    responsabilites = models.TextField()

    def __str__(self):
        return f"Technicien: {self.utilisateur.username}"


# -----------------------------
# ADMINISTRATEUR
# -----------------------------
class Administrateur(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='administrateur')
    administration = models.CharField(max_length=100)

    def __str__(self):
        return f"Administrateur: {self.utilisateur.username}"




# -----------------------------
# EQUIPEMENT (classe mère)
# -----------------------------
class Equipement(models.Model):
    TYPE_CHOICES = (
        ('INDIVIDUEL', 'Individuel'),
        ('DEPARTEMENTAL', 'Départemental'),
        ('RESEAU', 'Réseau'),
    )
    designation = models.CharField(max_length=100)
    fabriquant = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    etat = models.CharField(
        max_length=20,
        choices=[('DISPO', 'Disponible'), ('EN_PANNE', 'En panne'), ('MAINTENANCE', 'Maintenance')]
    )
    destination = models.CharField(max_length=100)
    localisation = models.CharField(max_length=100)
    date_livraison = models.DateField()
    duree_garantie = models.IntegerField()
    ip = models.GenericIPAddressField(null=True, blank=True)
    type_equipement = models.CharField(max_length=20, choices=TYPE_CHOICES)

    def __str__(self):
        return f"{self.designation} ({self.get_type_equipement_display()})"


# -----------------------------
# Equipement Individuel
# -----------------------------
class EquipementIndividuel(models.Model):
    equipement = models.OneToOneField(Equipement, on_delete=models.CASCADE, primary_key=True, related_name='individuel')
    TYPE_CHOICES = (
        ('PC', 'PC'),
        ('TABLETTE', 'Tablette'),
        ('PHONE', 'Téléphone'),
        ('SWITCH_LOCALE', 'Switch Locale'),
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date_affectation = models.DateField()
    date_mise_en_service = models.DateField()
    proprietaire = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='equipements_individuels')

    def __str__(self):
        return f"Equipement Individuel: {self.equipement.designation}"


# -----------------------------
# Equipement Departemental
# -----------------------------
class EquipementDepartemental(models.Model):
    equipement = models.OneToOneField(Equipement, on_delete=models.CASCADE, primary_key=True, related_name='departemental')
    TYPE_CHOICES = (
        ('ECRAN', 'Écran'),
        ('AFFICHAGE', 'Affichage'),
        ('SWITCH_RESEAU', 'Switch Réseau'),
        ('PC', 'PC'),
        ('TABLETTE', 'Tablette'),
        ('PHONE', 'Téléphone'),
        ('SWITCH_LOCALE', 'Switch Locale'),
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date_affectation = models.DateField()
    date_mise_en_service = models.DateField()
    emplacement = models.CharField(max_length=100)
    gerant = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='equipements_departementaux')
    service_attribue = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, related_name='equipements_departements')

    def __str__(self):
        return f"Equipement Départemental: {self.equipement.designation}"


# -----------------------------
# Equipement Reseau
# -----------------------------
class EquipementReseau(models.Model):
    equipement = models.OneToOneField(Equipement, on_delete=models.CASCADE, primary_key=True, related_name='reseau')
    TYPE_CHOICES = (
        ('SWITCH', 'Switch'),
        ('AP_WIFI', "Point d'accès Wi-Fi"),
        ('ROUTEUR', 'Routeur'),
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    adresse_mac = models.CharField(max_length=100)
    service_attribue = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, related_name='equipements_reseau')

    def __str__(self):
        return f"Equipement Réseau: {self.equipement.designation}"
 

# -----------------------------
# MAINTENANCE
# -----------------------------
class Maintenance(models.Model):
    equipement = models.ForeignKey(Equipement, on_delete=models.CASCADE, related_name='maintenances')
    technicien = models.ForeignKey(Technicien, on_delete=models.SET_NULL, null=True, related_name='maintenances')
    date = models.DateTimeField()
    description = models.TextField()

    def planifier(self):
        pass

    def __str__(self):
        return f"Maintenance de {self.equipement.designation} le {self.date}"


# -----------------------------
# ALERTE
# -----------------------------
class Alerte(models.Model):
    NIVEAU_CHOICES = (
        ('CRITIQUE', 'Critique'),
        ('WARNING', 'Avertissement'),
        ('INFO', 'Information'),
    )
    equipement = models.ForeignKey(Equipement, on_delete=models.CASCADE, related_name='alertes')
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES)
    resolue = models.BooleanField(default=False)

    def generer(self):
        pass

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"Alerte {self.niveau} pour {self.equipement.designation}"