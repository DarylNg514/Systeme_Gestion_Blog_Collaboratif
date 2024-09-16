from django.db import models
from django.contrib.auth.models import AbstractUser

# Modèle utilisateur personnalisé
class Utilisateur(AbstractUser):
    ROLE_CHOICES = (
        ('etudiant', 'Étudiant'),
        ('auteur_certifie', 'Auteur Certifié'),
        ('editeur', 'Éditeur'),
        ('admin', 'Admin'),
    )
    SEX_CHOICES = [
        ('Homme', 'Homme'),
        ('Femme', 'Femme'),
        ('Autre', 'Autre'),
    ]
    image = models.ImageField(upload_to='images/',  blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    sex = models.CharField(max_length=30, choices=SEX_CHOICES, null=True, blank=True)
    email = models.EmailField(unique=True)
    is_approved = models.BooleanField(null=True, default=None)  # null: en cours de vérification
    has_verified_identity = models.BooleanField(default=False)


# Modèle pour les certificats des auteurs
class Certification(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    document = models.FileField(upload_to='certifications/')
    est_approuve = models.BooleanField(null=True, default=None)  # null: en attente, False: rejeté

# Modèle pour les documents académiques des étudiants
class DocumentAcademique(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    document = models.FileField(upload_to='documents_academiques/')
    est_approuve = models.BooleanField(null=True, default=None)  # null: en attente, False: rejeté

# Modèle pour les catégories
class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom

# Modèle pour les tags
class Tag(models.Model):
    nom = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nom

# Modèle pour les articles
class Article(models.Model):
    titre = models.CharField(max_length=255)
    contenu = models.TextField()
    auteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='articles')
    cree_le = models.DateTimeField(auto_now_add=True)
    est_publie = models.BooleanField(null=True, default=None)
    categories = models.ManyToManyField(Categorie, related_name='articles')
    #tags = models.ManyToManyField(Tag, related_name='articles')
    statut_validation = models.CharField(max_length=20, default='en_attente')  # en_attente, approuve, rejete

    def __str__(self):
        return self.titre

# Modèle pour les commentaires
class Commentaire(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='commentaires')
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    contenu = models.TextField()
    cree_le = models.DateTimeField(auto_now_add=True)
    est_modere = models.BooleanField(default=False)

# Modèle pour les notifications
class Notification(models.Model):
    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    est_commentaire = models.BooleanField( blank=True, null=True, default=None)
    est_lu = models.BooleanField(default=False)
