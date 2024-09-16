# Generated by Django 5.1.1 on 2024-09-09 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_utilisateur_image_utilisateur_sex'),
    ]

    operations = [
        migrations.AlterField(
            model_name='utilisateur',
            name='sex',
            field=models.CharField(blank=True, choices=[('Homme', 'Homme'), ('Femme', 'Femme'), ('Autre', 'Autre')], max_length=30, null=True),
        ),
    ]
