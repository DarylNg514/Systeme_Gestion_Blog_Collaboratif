from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models import Q
from django.contrib import messages
from .models import *
from .forms import *

# Vue d'inscription
def inscription(request):
    if request.method == 'POST':
        form = FormulaireInscriptionUtilisateur(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()  # Enregistre l'utilisateur

            # Stocker l'ID de l'utilisateur nouvellement créé dans la session
            request.session['new_user_id'] = user.id

            # Redirige selon le rôle de l'utilisateur inscrit
            if user.role == 'auteur_certifie':
                return redirect('soumettre_certification')
            elif user.role == 'etudiant':
                return redirect('soumettre_document_academique')

    else:
        form = FormulaireInscriptionUtilisateur()
    return render(request, 'inscription.html', {'form': form})

# Vue de connexion avec vérification de l'approbation
def connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_approved is True:
                login(request, user)
                return redirect('dashboard')
            elif user.is_approved is False:
                messages.error(request, "Votre certification ou document académique a été rejeté. Veuillez recommencer l'inscription.")
                return redirect('inscription')  # Redirige vers l'inscription pour refaire le processus
            else:
                messages.info(request, "Votre certification ou document académique est en cours de vérification.")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    return render(request, 'connexion.html')
# Vue pour la gestion des articles

def acceuil(request):
    return render(request, 'acceuil.html')

def dashboard(request):
    # Filtrer les articles approuvés ou ceux de l'utilisateur s'il n'est pas admin
    if request.user.role == 'admin':  # Si l'utilisateur est administrateur, il voit tous les articles
        categories = Categorie.objects.prefetch_related(
            'articles'
        ).annotate(article_count=Count('articles'))
    else:
        categories = Categorie.objects.prefetch_related('articles').annotate(
            article_count=Count('articles', filter=(
                (Q(articles__est_publie=True) & Q(articles__statut_validation='approuve')) |
                Q(articles__auteur=request.user)
            ))
        )

    return render(request, 'dashboard.html', {
        'categories': categories,  # Toutes les catégories avec les articles associés
    })

    
def deconnexion(request):
    logout(request)
    return redirect('acceuil')


# Vue pour la soumission de la certification
def soumettre_certification(request):
    new_user_id = request.session.get('new_user_id')  # Récupérer l'ID de l'utilisateur stocké
    user = Utilisateur.objects.get(id=new_user_id)  # Récupérer l'utilisateur à partir de l'ID

    if request.method == 'POST':
        form = FormulaireCertification(request.POST, request.FILES)
        if form.is_valid():
            certification = form.save(commit=False)
            certification.utilisateur = user  # Associe la certification à l'utilisateur qui vient de s'inscrire
            certification.save()
            return render(request, 'soumis.html', {'message': "Votre certification a été soumise pour approbation."})
    else:
        form = FormulaireCertification()
    return render(request, 'soumettre.html', {'form': form})


# Vue pour la soumission d'un document académique
def soumettre_document_academique(request):
    new_user_id = request.session.get('new_user_id')  # Récupérer l'ID de l'utilisateur stocké
    user = Utilisateur.objects.get(id=new_user_id)  # Récupérer l'utilisateur à partir de l'ID

    if request.method == 'POST':
        form = FormulaireDocumentAcademique(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.utilisateur = user  # Associe le document académique à l'utilisateur qui vient de s'inscrire
            document.save()
            return render(request, 'soumis.html', {'message': "Votre document académique a été soumis pour approbation."})
    else:
        form = FormulaireDocumentAcademique()
    return render(request, 'soumettre.html', {'form': form})


@login_required
def soumettre_article(request):
    if request.method == 'POST':
        form = FormulaireArticle(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.auteur = request.user
            article.save()
            form.save_m2m()  # Pour enregistrer les relations ManyToMany
            return redirect('gerer_articles')
    else:
        form = FormulaireArticle()
    return render(request, 'soumettre_article.html', {'form': form})

@login_required
def liste_documents_a_approuver(request):
    if request.user.role == 'admin' or request.user.role == 'editeur':
        documents = DocumentAcademique.objects.filter(est_approuve=None)
        return render(request, 'liste_documents_a_approuver.html', {'documents': documents})
    else:
        return redirect('accueil')

@login_required
def liste_certifications_a_approuver(request):
    if request.user.role == 'admin' or request.user.role == 'editeur':
        certifications = Certification.objects.filter(est_approuve=None)
        return render(request, 'liste_certifications_a_approuver.html', {'certifications': certifications})
    else:
        return redirect('accueil')


@login_required
def approuver_certification(request, certification_id):
    if request.user.role == 'admin' or request.user.role == 'editeur':
        certification = get_object_or_404(Certification, id=certification_id)
        action = request.POST.get('action')

        if action == 'approuver':
            certification.est_approuve = True
            utilisateur = certification.utilisateur
            utilisateur.is_approved = True
            utilisateur.save()
            # Créer une notification pour informer l'utilisateur que sa certification a été approuvée
            Notification.objects.create(
            destinataire=utilisateur,
            message="Votre certification a été approuvée."
        )
            messages.success(request, "La certification a été approuvée.")
        elif action == 'rejeter':
            certification.est_approuve = False
            utilisateur = certification.utilisateur
            utilisateur.is_approved = False
            utilisateur.save()
            messages.error(request, "La certification a été rejetée.")
        
        certification.save()
        return redirect('liste_certifications_a_approuver')


@login_required
def approuver_document_academique(request, document_id):
    if request.user.role == 'admin' or request.user.role == 'editeur':
        document = get_object_or_404(DocumentAcademique, id=document_id)
        action = request.POST.get('action')

        if action == 'approuver':
            document.est_approuve = True
            utilisateur = document.utilisateur
            utilisateur.is_approved = True
            utilisateur.save()
            # Créer une notification pour informer l'utilisateur que son document académique a été approuvé
            Notification.objects.create(
            destinataire=utilisateur,
            message="Votre document académique a été approuvé."
        )
            messages.success(request, "Le document académique a été approuvé.")
        elif action == 'rejeter':
            document.est_approuve = False
            utilisateur = document.utilisateur
            utilisateur.is_approved = False
            utilisateur.save()
            messages.error(request, "Le document académique a été rejeté.")
        
        document.save()
        return redirect('liste_documents_a_approuver')

# Créer une nouvelle catégorie
def creer_categorie(request):
    if request.method == 'POST':
        form = FormulaireCategorie(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = FormulaireCategorie()
    return render(request, 'creation.html', {'form': form})

# Lire/Afficher la liste des catégories
def liste_categories(request):
    categories = Categorie.objects.all()
    return render(request, 'dashboard.html', {'categories': categories})

# Mettre à jour une catégorie existante
def modifier_categorie(request, pk):
    categorie = get_object_or_404(Categorie, pk=pk)
    if request.method == 'POST':
        form = FormulaireCategorie(request.POST, instance=categorie)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = FormulaireCategorie(instance=categorie)
    return render(request, 'modification.html', {'form': form, 'categorie': categorie})

# Supprimer une catégorie
def supprimer_categorie(request, pk):
    categorie = get_object_or_404(Categorie, pk=pk)
    categorie.delete()
    return redirect('dashboard')

@login_required
def voir_notifications(request):
    notifications = Notification.objects.filter(destinataire=request.user, est_lu=False).order_by('-date_creation')
    return render(request, 'notifications.html', {'notifications': notifications})

@login_required
def marquer_comme_lu(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, destinataire=request.user)
    notification.est_lu = True
    notification.save()

    # Vérifier si la notification est liée à un commentaire et récupérer l'article associé
    if notification.est_commentaire:
        commentaire = Commentaire.objects.filter(utilisateur=request.user).first()
        if commentaire:
            return redirect('article_commentaire', article_id=commentaire.article.id)  # Rediriger avec l'ID de l'article
        else:
            return redirect('dashboard') 
    else:
        return redirect('dashboard')


@login_required
def supprimer_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, destinataire=request.user)
    notification.delete()
    return redirect('voir_notifications')

@login_required
def supprimer_toutes_les_notifications(request):
    Notification.objects.filter(destinataire=request.user).delete()
    return redirect('voir_notifications')
    
@login_required
def publier_article(request, article_id):
    if request.user.role in ['auteur_certifie', 'etudiant', 'admin', 'editeur'] or request.user == article.auteur:
        article = get_object_or_404(Article, id=article_id)
        article.est_publie = True
        if request.user.role in ['auteur_certifie', 'admin', 'editeur']:
            article.statut_validation = 'approuve'  # Marquer l'article comme approuvé
            article.save()

            # Envoyer une notification à l'auteur
            Notification.objects.create(
                destinataire=article.auteur,
                message=f'Votre article "{article.titre}" a été publié.'
            )

            # Envoyer une notification à tous les autres utilisateurs
            utilisateurs = Utilisateur.objects.exclude(id=article.auteur.id)
            for utilisateur in utilisateurs:
                Notification.objects.create(
                    destinataire=utilisateur,
                    message=f'Un nouvel article intitulé "{article.titre}" a été publié.'
                )
            
            messages.success(request, 'L\'article a été publié avec succès et tous les utilisateurs ont été notifiés.')

            
        else:
            article.save()

            # Envoyer une notification à l'auteur
            Notification.objects.create(
                destinataire=article.auteur,
                message=f'Votre article "{article.titre}" a été envoyé pour révision par le comité éditorial.'
            )
            # Envoyer une notification à tous les éditeurs
            editeurs = Utilisateur.objects.filter(role='editeur')
            for editeur in editeurs:
                Notification.objects.create(
                    destinataire=editeur,
                    message=f'L\'article "{article.titre}" a été envoyé pour révision par l\'{article.auteur.role} {article.auteur}.'
                )

            messages.success(request, 'L\'article a été envoyé pour révision par le comité éditorial.')
        return redirect('dashboard')
    else:
        return redirect('permission_refusee')

@login_required
def depublier_article(request, article_id):
    article = get_object_or_404(Article, id=article_id, est_publie=True)

    if request.user.role in ['auteur_certifie', 'etudiant', 'admin', 'editeur'] or request.user == article.auteur:
        article.est_publie = False
        article.statut_validation = 'en_attente'  # Marquer l'article comme dépublié
        article.save()

        # Envoyer une notification à l'auteur
        Notification.objects.create(
            destinataire=article.auteur,
            message=f'Votre article "{article.titre}" a été retiré de la publication.'
        )

        # Envoyer une notification à tous les autres utilisateurs
        utilisateurs = Utilisateur.objects.exclude(id=article.auteur.id)
        for utilisateur in utilisateurs:
            Notification.objects.create(
                destinataire=utilisateur,
                message=f'L\'article "{article.titre}" a été retiré de la publication.'
            )

        messages.success(request, f'L\'article "{article.titre}" a été retiré de la publication.')
        return redirect('dashboard')
    else:
        return redirect('permission_refusee')


    
@login_required
def article_commentaire(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    commentaires = article.commentaires.all()  # Récupérer les commentaires de l'article

    if request.method == 'POST':
        form = FormulaireCommentaire(request.POST)
        if form.is_valid():
            nouveau_commentaire = form.save(commit=False)
            nouveau_commentaire.article = article
            nouveau_commentaire.utilisateur = request.user
            nouveau_commentaire.save()

            # Créer une notification pour l'auteur de l'article
            Notification.objects.create(
                destinataire=article.auteur,
                message=f"Vous avez reçu un nouveau commentaire sur votre article '{article.titre}'.",
                est_commentaire=True
                
            )

            return redirect('article_commentaire', article_id=article.id)
    else:
        form = FormulaireCommentaire()

    return render(request, 'article_commentaire.html', {
        'article': article,
        'commentaires': commentaires,
        'user': request.user,
        'form': form
    })


@login_required
def modifier_commentaire(request, commentaire_id):
    commentaire = get_object_or_404(Commentaire, id=commentaire_id, utilisateur=request.user)

    if request.method == 'POST':
        form = FormulaireCommentaire(request.POST, instance=commentaire)
        if form.is_valid():
            form.save()

            # Créer une notification pour l'auteur de l'article
            Notification.objects.create(
                destinataire=commentaire.article.auteur,
                message=f"Un commentaire sur votre article '{commentaire.article.titre}' a été modifié.",
                est_commentaire=True
            )

            return redirect('article_commentaire', article_id=commentaire.article.id)
    else:
        form = FormulaireCommentaire(instance=commentaire)

    return render(request, 'modifier_commentaire.html', {'form': form})

@login_required
def supprimer_commentaire(request, commentaire_id):
    commentaire = get_object_or_404(Commentaire, id=commentaire_id, utilisateur=request.user)
    article_id = commentaire.article.id
    commentaire.delete()
    return redirect('article_commentaire', article_id=article_id)

    
@login_required
def creer_article(request, categorie_id=None):
    categorie = get_object_or_404(Categorie, id=categorie_id) if categorie_id else None
    
    # Vérifie si l'utilisateur est un auteur certifié, étudiant ou administrateur
    if request.user.role in ['auteur_certifie', 'etudiant', 'admin', 'editeur']:
        if request.method == 'POST':
            if request.user.role in ['admin', 'editeur'] and 'auteur' in request.POST:
                # Formulaire pour administrateur qui peut sélectionner un auteur pour l'article
                form = FormulaireArticle(request.POST)
                if form.is_valid():
                    article = form.save(commit=False)
                    article.est_publie = True
                    article.statut_validation = 'approuve'
                    # Assigner l'utilisateur sélectionné par l'admin
                    article.auteur = Utilisateur.objects.get(id=request.POST['auteur'])
                    article.save()
            else:
                # Formulaire pour auteur certifié ou étudiant
                form = FormulaireArticle2(request.POST)
                if form.is_valid():
                    article = form.save(commit=False)
                    article.auteur = request.user
                    article.save()

            # Ajouter la catégorie à l'article s'il y en a une
            if categorie:
                article.categories.add(categorie)
            
            return redirect('dashboard')
        else:
            # Initialiser le formulaire
            form = FormulaireArticle() if request.user.role == 'admin' else FormulaireArticle2()

        # Si l'utilisateur est un admin, permettre la sélection d'un utilisateur
        utilisateurs = Utilisateur.objects.all() if request.user.role == 'admin' else None
        
        return render(request, 'creation.html', {
            'form': form, 
            'categorie': categorie, 
            'utilisateurs': utilisateurs
        })
    else:
        # Rediriger si l'utilisateur n'a pas les droits nécessaires
        return redirect('permission_refusee')
    
@login_required
def modifier_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    # Seuls l'auteur ou l'admin peuvent modifier
    if request.user == article.auteur or request.user.role == 'admin':
        if request.method == 'POST':
            form = FormulaireArticle(request.POST, instance=article)
            if form.is_valid():
                form.save()
                return redirect('article_commentaire', article_id=article.id)
        else:
            form = FormulaireArticle(instance=article)

        return render(request, 'modification.html', {'form': form, 'article': article})
    else:
        return redirect('permission_refusee')  # Si l'utilisateur n'est pas autorisé


@login_required
def supprimer_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    # Seuls l'auteur ou l'admin peuvent supprimer
    if request.user == article.auteur or request.user.role == 'admin':
        article.delete()
        return redirect('dashboard')  # Redirection après suppression
    else:
        return redirect('permission_refusee')  # Si l'utilisateur n'est pas autorisé


@login_required
def soumettre_article(request):
    if request.user.role == 'etudiant':
        if request.method == 'POST':
            form = FormulaireArticle(request.POST)
            if form.is_valid():
                article = form.save(commit=False)
                article.auteur = request.user
                article.est_publie = True  # L'article attend la révision
                article.save()
                return redirect('dashboard')  # Redirige vers la liste des articles après soumission
        else:
            form = FormulaireArticle()
        return render(request, 'soumettre_article.html', {'form': form})
    else:
        return redirect('permission_refusee')  # Redirige si l'utilisateur n'est pas un étudiant

@login_required
def liste_articles_en_attente(request):
    if request.user.is_superuser or request.user.role in ['admin', 'editeur']:
        # Récupérer les articles en attente de validation
        articles_en_attente = Article.objects.filter(est_publie=True, statut_validation='en_attente')

        return render(request, 'articles_en_attente.html', {
            'articles': articles_en_attente 
        })
    else:
        return render(request, 'permission_refusee.html')

@login_required
def valider_article(request, article_id):
    if request.user.role == 'editeur':
        article = get_object_or_404(Article, id=article_id, est_publie=True,statut_validation = 'en_attente')  # En attente de validation
        
        if request.method == 'POST':
            # Valider l'article
            if 'valider' in request.POST:
                article.est_publie = True
                article.statut_validation = 'approuve'
                article.save()
                
                # Créer une notification de rejet avec commentaire
                commentaire = request.POST.get('commentaire', '')
                Notification.objects.create(
                    destinataire=article.auteur,  # L'auteur de l'article reçoit la notification
                    message=f"Votre article '{article.titre}' a été valider et publier.",
                )
                messages.success(request, f"L'article '{article.titre}' a été validé.")
                return redirect('dashboard')
            
            # Rejeter l'article
            if 'rejeter' in request.POST:
                article.est_publie = False
                article.statut_validation = 'rejete'
                article.save()

                # Créer une notification de rejet avec commentaire
                commentaire = request.POST.get('commentaire', '')
                Notification.objects.create(
                    destinataire=article.auteur,  # L'auteur de l'article reçoit la notification
                    message=f"Votre article '{article.titre}' a été rejeté pour les raisons ci dessous : \n {commentaire} ",
                )
                messages.error(request, f"L'article '{article.titre}' a été rejeté.")
                return redirect('dashboard')
        
        return render(request, 'valider.html', {'article': article})
    
    else:
        return redirect('permission_refusee')
    
@login_required
def liste_utilisateurs(request):
    if request.user.role == 'admin':
        utilisateurs = Utilisateur.objects.all()
        return render(request, 'liste_utilisateurs.html', {'utilisateurs': utilisateurs})
    else:
        return redirect('permission_refusee')  # Redirige si l'utilisateur n'est pas un administrateur

@login_required   
def ajouter_utilisateur(request):
    if request.user.role == 'admin':
        if request.method == 'POST':
            form = FormulaireAjoutUtilisateur(request.POST, request.FILES)
            if form.is_valid():
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password1'])
                user.is_approved = True
                user.has_verified_identity = True
                if user.role == 'admin':
                    user.is_staff = True
                    user.is_superuser = True
                user.save()  # Enregistre l'utilisateur
                return redirect('liste_utilisateurs')  # Redirige vers la liste des utilisateurs après ajout
        else:
            form = FormulaireAjoutUtilisateur()
        return render(request, 'inscription.html', {'form': form})    
    else:
        return redirect('permission_refusee')  # Redirige si l'utilisateur n'est pas un administrateur

    
@login_required
def modifier_utilisateur(request, utilisateur_id):
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
    if request.user.role == 'admin':
        if request.method == 'POST':
            form = FormulaireAjoutUtilisateur(request.POST, request.FILES, instance=utilisateur)
            if form.is_valid():
                form.save()
                messages.success(request, "Utilisateur modifié avec succès.")
                return redirect('liste_utilisateurs')
        else:
            form = FormulaireAjoutUtilisateur(instance=utilisateur)
        
        return render(request, 'modification.html', {'form': form})
    else:
        return redirect('permission_refusee')  # Redirige si l'utilisateur n'est pas un administrateur

@login_required
def supprimer_utilisateur(request, utilisateur_id):
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
    if request.user.role == 'admin':
        utilisateur.delete()
        messages.success(request, "Utilisateur supprimé avec succès.")
        return redirect('liste_utilisateurs')
    else:
        return redirect('permission_refusee')  # Redirige si l'utilisateur n'est pas un administrateur

@login_required
def afficher_mes_informations(request):
    utilisateur = request.user  # Récupérer l'utilisateur connecté
    return render(request, 'afficher_mes_informations.html', {'utilisateur': utilisateur})

@login_required
def modifier_mon_compte(request):
    utilisateur = request.user  # Récupérer l'utilisateur connecté

    if request.method == 'POST':
        if utilisateur.role == 'admin':
            form = FormulaireAjoutUtilisateur(request.POST, request.FILES, instance=utilisateur)
        else:
            form = FormulaireModifierUtilisateur(request.POST, request.FILES, instance=utilisateur)
        if form.is_valid():
            form.save()
            messages.success(request, "Vos informations ont été modifiées avec succès.")
            return redirect('dashboard')  # Redirige vers le tableau de bord ou autre
    else:
        if utilisateur.role == 'admin':
            form = FormulaireAjoutUtilisateur(instance=utilisateur)
        else:
            form = FormulaireModifierUtilisateur(instance=utilisateur)
        

    return render(request, 'modification.html', {'form': form})

@login_required
def supprimer_mon_compte(request):
    utilisateur = request.user
    if request.method == 'POST':
        utilisateur.delete()
        messages.success(request, "Votre compte a été supprimé avec succès.")
        return redirect('index')  # Redirige vers la page d'accueil après suppression
    return render(request, 'supprimer_mon_compte.html', {'utilisateur': utilisateur})





'''
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, ArticleForm, CommentForm, CertificationForm
from .models import Article, Comment, Certification, ArticleReview, Notification




@login_required
def changer_role(request, utilisateur_id):
    if request.user.role == 'admin':
        utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
        if request.method == 'POST':
            nouveau_role = request.POST.get('role')
            utilisateur.role = nouveau_role
            utilisateur.save()
            return redirect('gerer_utilisateurs')  # Redirige vers la liste des utilisateurs après modification
        return render(request, 'changer_role.html', {'utilisateur': utilisateur})
    else:
        return redirect('permission_refusee')
    




@login_required
def editer_article(request, pk):
    article = get_object_or_404(Article, pk=pk, auteur=request.user)
    if request.method == 'POST':
        form = FormulaireArticle(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('gerer_articles')
    else:
        form = FormulaireArticle(instance=article)
    return render(request, 'editer_article.html', {'form': form})

# Vue pour l'inscription des utilisateurs
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.is_author:
                messages.info(request, "Vous devez soumettre vos certifications.")
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

# Vue pour soumettre un document de certification
@login_required
def submit_certification(request):
    if request.method == 'POST':
        form = CertificationForm(request.POST, request.FILES)
        if form.is_valid():
            certification = form.save(commit=False)
            certification.user = request.user
            certification.save()
            messages.success(request, "Document soumis pour validation.")
            return redirect('dashboard')
    else:
        form = CertificationForm()
    return render(request, 'certifications/submit.html', {'form': form})

# Vue pour créer un article
@login_required
def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, "Article créé avec succès.")
            return redirect('article_detail', pk=article.pk)
    else:
        form = ArticleForm()
    return render(request, 'articles/create_article.html', {'form': form})

# Vue pour soumettre un article étudiant pour révision
@login_required
def submit_student_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, "Article soumis pour révision.")
            return redirect('article_list')
    else:
        form = ArticleForm()
    return render(request, 'articles/submit_student_article.html', {'form': form})

# Vue pour la revue et la validation des articles par le comité éditorial
@login_required
def review_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        comments = request.POST.get('comments')
        is_approved = 'approve' in request.POST
        review = ArticleReview.objects.create(article=article, reviewer=request.user, comments=comments, is_approved=is_approved)
        if is_approved:
            article.is_published = True
            article.save()
            messages.success(request, "L'article a été approuvé et publié.")
        else:
            messages.warning(request, "L'article a été rejeté.")
        return redirect('article_list')
    return render(request, 'articles/review_article.html', {'article': article})

# Vue pour l'ajout de commentaires
@login_required
def add_comment(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.user = request.user
            comment.save()
            messages.success(request, "Commentaire ajouté.")
            return redirect('article_detail', pk=article.pk)
    else:
        form = CommentForm()
    return render(request, 'comments/add_comment.html', {'form': form})
    
def articles_par_categorie(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    articles = categorie.articles.filter(est_publie=True)
    return render(request, 'articles/articles_par_categorie.html', {'categorie': categorie, 'articles': articles})

def articles_par_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    articles = tag.articles.filter(est_publie=True)
    return render(request, 'articles/articles_par_tag.html', {'tag': tag, 'articles': articles})


@login_required
def soumettre_article(request):
    if request.method == 'POST':
        form = FormulaireArticle(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.auteur = request.user
            article.save()
            form.save_m2m()  # Pour enregistrer les relations ManyToMany
            return redirect('gerer_articles')
    else:
        form = FormulaireArticle()
    return render(request, 'articles/soumettre_article.html', {'form': form})

@login_required
def editer_article(request, pk):
    article = get_object_or_404(Article, pk=pk, auteur=request.user)
    if request.method == 'POST':
        form = FormulaireArticle(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('gerer_articles')
    else:
        form = FormulaireArticle(instance=article)
    return render(request, 'articles/editer_article.html', {'form': form})


@login_required
def recherche_avancee(request):
    query = request.GET.get('q')
    articles = Article.objects.filter(titre__icontains=query) | Article.objects.filter(contenu__icontains=query)
    return render(request, 'recherche/recherche_resultats.html', {'articles': articles})
    
@login_required
def valider_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        est_approuve = 'approuver' in request.POST
        revue = RevueArticle.objects.create(article=article, validateur=request.user, est_approuve=est_approuve, commentaires=request.POST['commentaires'])
        article.statut_validation = 'approuve' if est_approuve else 'rejete'
        article.est_publie = est_approuve
        article.save()
        Notification.objects.create(destinataire=article.auteur, message=f"Votre article a été {'approuvé' if est_approuve else 'rejeté'}")
        return redirect('tableau_de_bord')
    return render(request, 'articles/valider_article.html', {'article': article})


@login_required
def ajouter_commentaire(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        contenu = request.POST['contenu']
        Commentaire.objects.create(article=article, utilisateur=request.user, contenu=contenu)
        return redirect('detail_article', pk=article.pk)
    return render(request, 'commentaires/ajouter_commentaire.html', {'article': article})

@login_required
def moderer_commentaires(request):
    if request.user.role != 'admin' and request.user.role != 'editeur':
        return redirect('accueil')
    commentaires = Commentaire.objects.filter(est_modere=False)
    return render(request, 'admin/moderer_commentaires.html', {'commentaires': commentaires})


'''