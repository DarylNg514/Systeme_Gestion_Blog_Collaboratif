from django import forms
from .models import *

# Formulaire d'inscription
class FormulaireInscriptionUtilisateur(forms.ModelForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        max_length=150,
        help_text='',  # Supprime le message "Required..."
    )
    first_name = forms.CharField(label="Prenom")
    last_name = forms.CharField(label="Nom")
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmez le mot de passe", widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=[('etudiant', 'Étudiant'), ('auteur_certifie', 'Auteur Certifié')])
    sex = forms.ChoiceField(choices=Utilisateur.SEX_CHOICES, required=True)


    class Meta:
        model = Utilisateur
        fields = ['username', 'email','first_name', 'last_name', 'password1', 'password2', 'role','sex','image']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return password2
    
class FormulaireAjoutUtilisateur(forms.ModelForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        max_length=150,
        help_text='',  # Supprime le message "Required..."
    )
    first_name = forms.CharField(label="Prenom")
    last_name = forms.CharField(label="Nom")
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmez le mot de passe", widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=Utilisateur.ROLE_CHOICES)  # Administrateur peut choisir le rôle
    sex = forms.ChoiceField(choices=Utilisateur.SEX_CHOICES, required=True)

    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'sex', 'image']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return password2


class FormulaireModifierUtilisateur(forms.ModelForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        max_length=150,
        help_text='',  # Supprime le message "Required..."
    )
    first_name = forms.CharField(label="Prenom")
    last_name = forms.CharField(label="Nom")
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmez le mot de passe", widget=forms.PasswordInput)
    sex = forms.ChoiceField(choices=Utilisateur.SEX_CHOICES, required=True)

    class Meta:
        model = Utilisateur
        fields = ['username', 'email','first_name', 'last_name', 'password1', 'password2','sex','image']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return password2

# Formulaire pour soumettre un certificat ou un document académique
class FormulaireCertification(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['document']

class FormulaireDocumentAcademique(forms.ModelForm):
    class Meta:
        model = DocumentAcademique
        fields = ['document']
        
class FormulaireArticle(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['titre', 'contenu']

    # Ajouter une liste déroulante pour les administrateurs
    auteur = forms.ModelChoiceField(queryset=Utilisateur.objects.all(), required=False, label="Sélectionner l'auteur", empty_label="Sélectionnez un utilisateur")

# Formulaire pour créer ou éditer un article
class FormulaireArticle2(forms.ModelForm):
    #categories = forms.ModelMultipleChoiceField(queryset=Categorie.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)
    #tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Article
        fields = ['titre', 'contenu']

# Formulaire pour ajouter des commentaires
class FormulaireCommentaire(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['contenu']

class FormulaireCategorie(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'description']