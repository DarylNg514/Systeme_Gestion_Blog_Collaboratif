# Generated by Django 5.1.1 on 2024-09-09 21:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_remove_utilisateur_sex'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='utilisateur',
            name='image',
        ),
    ]
