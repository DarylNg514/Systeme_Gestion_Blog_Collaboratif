from django.contrib import admin
from .models import *

# Register your models here.
# Enregistrement des modèles dans l'interface admin
admin.site.register(Utilisateur)
admin.site.register(Certification)
admin.site.register(DocumentAcademique)
admin.site.register(Article)
admin.site.register(Categorie)
admin.site.register(Notification)
admin.site.register(Commentaire)
admin.site.register(Tag)