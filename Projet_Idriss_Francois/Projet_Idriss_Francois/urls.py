"""
URL configuration for Projet_Idriss_Francois project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
    
        
     '''
    path('register/', views.register, name='register'),
    path('certification/submit/', views.submit_certification, name='submit_certification'),
    path('article/create/', views.create_article, name='create_article'),
    path('article/submit/', views.submit_student_article, name='submit_student_article'),
    path('article/<int:pk>/review/', views.review_article, name='review_article'),
    path('article/<int:article_id>/comment/', views.add_comment, name='add_comment'),
    '''
    
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from users import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.acceuil, name='acceuil'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('certification/soumettre/', views.soumettre_certification, name='soumettre_certification'),
    path('document_academique/soumettre/', views.soumettre_document_academique, name='soumettre_document_academique'),
    path('article/soumettre/', views.soumettre_article, name='soumettre_article'),
    path('certifications/', views.liste_certifications_a_approuver, name='liste_certifications_a_approuver'),
    path('documents_academiques/', views.liste_documents_a_approuver, name='liste_documents_a_approuver'),
    path('certification/approuver/<int:certification_id>/', views.approuver_certification, name='approuver_certification'),
    path('document_academique/approuver/<int:document_id>/', views.approuver_document_academique, name='approuver_document_academique'),
    path('categories/', views.liste_categories, name='liste_categories'),
    path('creer-categorie/', views.creer_categorie, name='creer_categorie'),  # Route pour la création de catégorie
    path('categories/creer/', views.creer_categorie, name='creer_categorie'),
    path('categories/modifier/<int:pk>/', views.modifier_categorie, name='modifier_categorie'),
    path('categories/supprimer/<int:pk>/', views.supprimer_categorie, name='supprimer_categorie'),
    path('notifications/', views.voir_notifications, name='voir_notifications'),
    path('notifications/marquer_comme_lu/<int:notification_id>/', views.marquer_comme_lu, name='marquer_comme_lu'),
    path('notifications/supprimer/<int:notification_id>/', views.supprimer_notification, name='supprimer_notification'),
    path('notifications/supprimer_toutes/', views.supprimer_toutes_les_notifications, name='supprimer_toutes_les_notifications'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('commentaire/<int:article_id>/', views.article_commentaire, name='article_commentaire'),
    path('modifier_commentaire/<int:commentaire_id>/', views.modifier_commentaire, name='modifier_commentaire'),
    path('supprimer_commentaire/<int:commentaire_id>/', views.supprimer_commentaire, name='supprimer_commentaire'),
    # Route pour créer un article dans une catégorie spécifique
    path('creer-article/<int:categorie_id>/', views.creer_article, name='creer_article'),
    path('article/modifier/<int:article_id>/', views.modifier_article, name='modifier_article'),
    path('article/supprimer/<int:article_id>/', views.supprimer_article, name='supprimer_article'),
    path('articles-en-attente/', views.liste_articles_en_attente, name='liste_articles_en_attente'),
    path('publier-article/<int:article_id>/', views.publier_article, name='publier_article'),
    path('depublier-article/<int:article_id>/', views.depublier_article, name='depublier_article'),
    path('valider-article/<int:article_id>/', views.valider_article, name='valider_article'),
    # Route pour créer un article sans catégorie (optionnel)liste_articles_en_attente
    path('utilisateurs/', views.liste_utilisateurs, name='liste_utilisateurs'),
    path('ajouter-utilisateur/', views.ajouter_utilisateur, name='ajouter_utilisateur'),
    path('utilisateurs/modifier/<int:utilisateur_id>/', views.modifier_utilisateur, name='modifier_utilisateur'),
    path('utilisateurs/supprimer/<int:utilisateur_id>/', views.supprimer_utilisateur, name='supprimer_utilisateur'),
    path('mon_compte/informations/', views.afficher_mes_informations, name='afficher_mes_informations'),
    path('mon_compte/modifier/', views.modifier_mon_compte, name='modifier_mon_compte'),
    path('mon_compte/supprimer/', views.supprimer_mon_compte, name='supprimer_mon_compte'),
]
if settings.DEBUG:  # Ajoutez cette condition pour les fichiers médias en mode développement
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

